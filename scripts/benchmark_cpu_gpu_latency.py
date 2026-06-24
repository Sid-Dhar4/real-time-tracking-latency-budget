#!/usr/bin/env python3

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import pandas as pd
import torch
import yaml
from ultralytics import YOLO


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    idx = round((q / 100.0) * (len(xs) - 1))
    return float(xs[int(idx)])


def load_frames(image_dir: Path, max_frames: int) -> list[tuple[str, object]]:
    image_paths = sorted(image_dir.glob("*.png"))
    if max_frames > 0:
        image_paths = image_paths[:max_frames]

    if not image_paths:
        raise FileNotFoundError(f"No PNG images found in {image_dir}")

    frames = []
    for path in image_paths:
        image = cv2.imread(str(path))
        if image is None:
            raise RuntimeError(f"Failed to read image: {path}")
        frames.append((path.name, image))

    return frames


def sync_if_gpu(device_label: str) -> None:
    if device_label == "gpu" and torch.cuda.is_available():
        torch.cuda.synchronize()


def run_device(
    *,
    device_label: str,
    ultralytics_device,
    weights: str,
    frames: list[tuple[str, object]],
    imgsz: int,
    conf: float,
    iou: float,
    warmup_frames: int,
) -> list[dict]:
    model = YOLO(weights)

    warmup = min(warmup_frames, len(frames))
    for _, image in frames[:warmup]:
        _ = model.predict(
            source=image,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            device=ultralytics_device,
            verbose=False,
        )
    sync_if_gpu(device_label)

    rows = []
    for frame_index, (image_name, image) in enumerate(frames):
        sync_if_gpu(device_label)
        start = time.perf_counter()
        results = model.predict(
            source=image,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            device=ultralytics_device,
            verbose=False,
        )
        sync_if_gpu(device_label)
        latency_ms = (time.perf_counter() - start) * 1000.0

        boxes = results[0].boxes
        det_count = 0 if boxes is None else len(boxes)

        rows.append(
            {
                "device": device_label,
                "frame_index": frame_index,
                "image_name": image_name,
                "latency_ms": latency_ms,
                "detection_count": det_count,
            }
        )

    return rows


def summarize(raw: pd.DataFrame, warmup_frames: int) -> pd.DataFrame:
    rows = []

    for device, group in raw.groupby("device"):
        latencies = group["latency_ms"].astype(float).tolist()
        mean_ms = float(pd.Series(latencies).mean())
        median_ms = float(pd.Series(latencies).median())
        p95_ms = percentile(latencies, 95.0)
        fps = 1000.0 / mean_ms if mean_ms > 0 else 0.0

        rows.append(
            {
                "device": device,
                "frames": len(latencies),
                "warmup_frames": warmup_frames,
                "mean_latency_ms": mean_ms,
                "median_latency_ms": median_ms,
                "p95_latency_ms": p95_ms,
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "fps_from_mean": fps,
                "meets_30hz_mean": mean_ms <= 33.33,
                "meets_30hz_p95": p95_ms <= 33.33,
                "meets_60hz_mean": mean_ms <= 16.67,
                "meets_60hz_p95": p95_ms <= 16.67,
            }
        )

    summary = pd.DataFrame(rows).sort_values("device").reset_index(drop=True)

    if {"cpu", "gpu"}.issubset(set(summary["device"])):
        cpu_mean = float(summary.loc[summary["device"] == "cpu", "mean_latency_ms"].iloc[0])
        gpu_mean = float(summary.loc[summary["device"] == "gpu", "mean_latency_ms"].iloc[0])
        cpu_p95 = float(summary.loc[summary["device"] == "cpu", "p95_latency_ms"].iloc[0])
        gpu_p95 = float(summary.loc[summary["device"] == "gpu", "p95_latency_ms"].iloc[0])

        summary["gpu_speedup_vs_cpu_mean"] = cpu_mean / gpu_mean if gpu_mean > 0 else 0.0
        summary["gpu_speedup_vs_cpu_p95"] = cpu_p95 / gpu_p95 if gpu_p95 > 0 else 0.0
    else:
        summary["gpu_speedup_vs_cpu_mean"] = 0.0
        summary["gpu_speedup_vs_cpu_p95"] = 0.0

    return summary


def make_plot(summary: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    plot_df = summary.set_index("device")[["mean_latency_ms", "p95_latency_ms"]]
    ax = plot_df.plot(kind="bar", figsize=(7, 4.5))
    ax.set_title("YOLOv8n latency: CPU vs GPU")
    ax.set_xlabel("device")
    ax.set_ylabel("latency_ms")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure YOLOv8n CPU vs GPU inference latency on KITTI frames.")
    parser.add_argument("--config", type=Path, default=Path("configs/detector/yolov8n.yaml"))
    parser.add_argument("--max-frames", type=int, default=100)
    parser.add_argument("--warmup-frames", type=int, default=5)
    parser.add_argument("--raw-output", type=Path, default=Path("results/tables/m36_cpu_gpu_latency_raw.csv"))
    parser.add_argument("--summary-output", type=Path, default=Path("results/tables/m36_cpu_gpu_latency_summary.csv"))
    parser.add_argument("--plot-output", type=Path, default=Path("results/plots/m36_cpu_gpu_latency_comparison.png"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    detector_cfg = cfg["detector"]
    dataset_cfg = cfg["dataset"]

    weights = detector_cfg["weights"]
    imgsz = int(detector_cfg["image_size"])
    conf = float(detector_cfg["confidence_threshold"])
    iou = float(detector_cfg["iou_threshold"])
    image_dir = Path(dataset_cfg["image_dir"])

    frames = load_frames(image_dir, args.max_frames)

    all_rows = []

    # Run GPU first. Some inference libraries modify CUDA visibility when
    # selecting CPU mode, so the GPU pass should happen before any CPU-only pass.
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available, cannot run GPU benchmark.")

    all_rows.extend(
        run_device(
            device_label="gpu",
            ultralytics_device=0,
            weights=weights,
            frames=frames,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            warmup_frames=args.warmup_frames,
        )
    )

    all_rows.extend(
        run_device(
            device_label="cpu",
            ultralytics_device="cpu",
            weights=weights,
            frames=frames,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            warmup_frames=args.warmup_frames,
        )
    )

    raw = pd.DataFrame(all_rows)
    summary = summarize(raw, args.warmup_frames)

    args.raw_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)

    raw.to_csv(args.raw_output, index=False)
    summary.to_csv(args.summary_output, index=False)
    make_plot(summary, args.plot_output)

    print("wrote", args.raw_output, "rows", len(raw))
    print("wrote", args.summary_output)
    print(summary.round(3).to_string(index=False))
    print("wrote", args.plot_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import importlib.util
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from tqdm import tqdm
from ultralytics import YOLO


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_eval_module():
    module_path = Path("scripts/evaluate_local_kitti.py")
    spec = importlib.util.spec_from_file_location("evaluate_local_kitti", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load evaluator module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_tracker_for_threshold(
    model: YOLO,
    image_paths: list[Path],
    sequence: str,
    threshold: float,
    tracker_config: str,
    device: str,
    imgsz: int,
    iou_threshold: float,
    output_csv: Path,
) -> dict:
    rows = []
    frame_latencies_ms = []
    unique_track_ids = set()

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    for frame_index, image_path in enumerate(tqdm(image_paths, desc=f"conf={threshold:.2f}")):
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"Failed to read image: {image_path}")

        start = time.perf_counter()
        results = model.track(
            source=image,
            imgsz=imgsz,
            conf=threshold,
            iou=iou_threshold,
            device=device,
            tracker=tracker_config,
            persist=True,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        frame_latencies_ms.append(elapsed_ms)

        result = results[0]

        if result.boxes is not None and result.boxes.id is not None:
            names = result.names

            for box in result.boxes:
                xyxy = box.xyxy[0].tolist()
                confidence = float(box.conf[0].item())
                class_id = int(box.cls[0].item())
                class_name = names[class_id]
                track_id = int(box.id[0].item())
                unique_track_ids.add(track_id)

                rows.append(
                    {
                        "sequence": sequence,
                        "frame": frame_index,
                        "image_name": image_path.name,
                        "track_id": track_id,
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "x1": float(xyxy[0]),
                        "y1": float(xyxy[1]),
                        "x2": float(xyxy[2]),
                        "y2": float(xyxy[3]),
                        "latency_ms": elapsed_ms,
                    }
                )

    fieldnames = [
        "sequence",
        "frame",
        "image_name",
        "track_id",
        "class_id",
        "class_name",
        "confidence",
        "x1",
        "y1",
        "x2",
        "y2",
        "latency_ms",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    mean_latency = sum(frame_latencies_ms) / len(frame_latencies_ms)
    sorted_latencies = sorted(frame_latencies_ms)
    p95_index = int(round(0.95 * (len(sorted_latencies) - 1)))
    p95_latency = sorted_latencies[p95_index]
    fps_estimate = 1000.0 / mean_latency if mean_latency > 0 else 0.0

    return {
        "tracks_csv": str(output_csv),
        "frames_processed": len(image_paths),
        "track_rows_written": len(rows),
        "unique_track_ids": len(unique_track_ids),
        "mean_latency_ms": mean_latency,
        "p95_latency_ms": p95_latency,
        "fps_estimate": fps_estimate,
    }


def make_plot(results_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.plot(results_df["mean_latency_ms"], results_df["idf1_like"], marker="o")

    for _, row in results_df.iterrows():
        plt.annotate(
            f"conf={row['confidence_threshold']:.2f}",
            (row["mean_latency_ms"], row["idf1_like"]),
            textcoords="offset points",
            xytext=(5, 5),
        )

    plt.xlabel("Mean latency per frame (ms, CPU)")
    plt.ylabel("IDF1-like score")
    plt.title("Confidence Threshold Sweep: Latency vs IDF1-like")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run confidence threshold sweep.")
    parser.add_argument("--config", type=Path, default=Path("configs/sweeps/confidence_sweep.yaml"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    eval_mod = load_eval_module()

    thresholds = [float(x) for x in cfg["sweep"]["values"]]

    dt_cfg = cfg["detector_tracker"]
    dataset_cfg = cfg["dataset"]
    outputs_cfg = cfg["outputs"]

    image_dir = Path(dataset_cfg["image_dir"])
    image_paths = sorted(image_dir.glob("*.png"))
    if not image_paths:
        raise FileNotFoundError(f"No images found in {image_dir}")

    sequence = str(dataset_cfg["sequence"])
    label_file = Path(dataset_cfg["label_file"])
    eval_class = str(dataset_cfg["eval_class"])
    eval_iou_threshold = float(dataset_cfg["eval_iou_threshold"])

    sweep_results_csv = Path(outputs_cfg["sweep_results_csv"])
    log_file = Path(outputs_cfg["log_file"])
    pareto_plot = Path(outputs_cfg["pareto_plot"])

    sweep_results_csv.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    model = YOLO(dt_cfg["detector_weights"])

    gt = eval_mod.load_kitti_gt(label_file, eval_class)

    all_rows = []
    log_lines = [
        "========== M5 CONFIDENCE THRESHOLD SWEEP ==========",
        f"config: {args.config}",
        f"sequence: {sequence}",
        f"image_dir: {image_dir}",
        f"label_file: {label_file}",
        f"eval_class: {eval_class}",
        f"eval_iou_threshold: {eval_iou_threshold}",
        f"thresholds: {thresholds}",
        "",
        "Important: local KITTI-style metrics, not official KITTI leaderboard metrics and not TrackEval HOTA.",
        "",
    ]

    for threshold in thresholds:
        safe_threshold = str(threshold).replace(".", "_")
        tracks_csv = Path(f"results/tracks/sweeps/yolov8n_bytetrack_seq{sequence}_conf_{safe_threshold}_tracks.csv")

        tracker_stats = run_tracker_for_threshold(
            model=model,
            image_paths=image_paths,
            sequence=sequence,
            threshold=threshold,
            tracker_config=dt_cfg["tracker_config"],
            device=dt_cfg["device"],
            imgsz=int(dt_cfg["image_size"]),
            iou_threshold=float(dt_cfg["iou_threshold"]),
            output_csv=tracks_csv,
        )

        pred = eval_mod.load_predictions(tracks_csv, eval_class)
        eval_results = eval_mod.evaluate(gt, pred, eval_iou_threshold)

        row = {
            "sequence": sequence,
            "confidence_threshold": threshold,
            "class_name": eval_class,
            "iou_threshold": eval_iou_threshold,
            "total_gt": eval_results["total_gt"],
            "total_pred": eval_results["total_pred"],
            "tp": eval_results["tp"],
            "fp": eval_results["fp"],
            "fn": eval_results["fn"],
            "id_switches": eval_results["id_switches"],
            "precision": eval_results["precision"],
            "recall": eval_results["recall"],
            "mota_like": eval_results["mota_like"],
            "idf1_like": eval_results["idf1_like"],
            "idtp_like": eval_results["idtp_like"],
            "idfp_like": eval_results["idfp_like"],
            "idfn_like": eval_results["idfn_like"],
            "frames_processed": tracker_stats["frames_processed"],
            "track_rows_written": tracker_stats["track_rows_written"],
            "unique_track_ids": tracker_stats["unique_track_ids"],
            "mean_latency_ms": tracker_stats["mean_latency_ms"],
            "p95_latency_ms": tracker_stats["p95_latency_ms"],
            "fps_estimate": tracker_stats["fps_estimate"],
            "tracks_csv": tracker_stats["tracks_csv"],
            "evaluator": "local_kitti_style_not_official_trackeval",
        }

        all_rows.append(row)

        log_lines.append(
            "conf={:.2f} precision={:.3f} recall={:.3f} idf1_like={:.3f} "
            "mota_like={:.3f} fp={} fn={} idsw={} mean_ms={:.2f} p95_ms={:.2f}".format(
                threshold,
                row["precision"],
                row["recall"],
                row["idf1_like"],
                row["mota_like"],
                row["fp"],
                row["fn"],
                row["id_switches"],
                row["mean_latency_ms"],
                row["p95_latency_ms"],
            )
        )

    results_df = pd.DataFrame(all_rows)
    results_df.to_csv(sweep_results_csv, index=False)
    make_plot(results_df, pareto_plot)

    log_lines.extend(
        [
            "",
            f"wrote_sweep_results: {sweep_results_csv}",
            f"wrote_pareto_plot: {pareto_plot}",
        ]
    )
    log_file.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("\n".join(log_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import cv2
import yaml
from tqdm import tqdm
from ultralytics import YOLO


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def draw_boxes(image, detections):
    for det in detections:
        x1, y1, x2, y2 = map(int, [det["x1"], det["y1"], det["x2"], det["y2"]])
        cls_name = det["class_name"]
        conf = det["confidence"]
        label = f"{cls_name} {conf:.2f}"

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            image,
            label,
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
    return image


def main() -> int:
    parser = argparse.ArgumentParser(description="Run YOLO detector on KITTI tracking frames.")
    parser.add_argument("--config", type=Path, default=Path("configs/detector/yolov8n.yaml"))
    parser.add_argument("--max-frames", type=int, default=10)
    args = parser.parse_args()

    cfg = load_config(args.config)

    detector_cfg = cfg["detector"]
    dataset_cfg = cfg["dataset"]
    outputs_cfg = cfg["outputs"]

    weights = detector_cfg["weights"]
    device = detector_cfg["device"]
    imgsz = int(detector_cfg["image_size"])
    conf = float(detector_cfg["confidence_threshold"])
    iou = float(detector_cfg["iou_threshold"])

    image_dir = Path(dataset_cfg["image_dir"])
    detections_csv = Path(outputs_cfg["detections_csv"])
    sample_visualization = Path(outputs_cfg["sample_visualization"])
    log_file = Path(outputs_cfg["log_file"])

    detections_csv.parent.mkdir(parents=True, exist_ok=True)
    sample_visualization.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(image_dir.glob("*.png"))
    if args.max_frames > 0:
        image_paths = image_paths[: args.max_frames]

    if not image_paths:
        raise FileNotFoundError(f"No PNG images found in {image_dir}")

    model = YOLO(weights)

    rows = []
    frame_latencies_ms = []
    first_frame_detections = None
    first_frame_image = None

    for frame_index, image_path in enumerate(tqdm(image_paths, desc="Running detector")):
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"Failed to read image: {image_path}")

        start = time.perf_counter()
        results = model.predict(
            source=image,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            device=device,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        frame_latencies_ms.append(elapsed_ms)

        frame_detections = []
        result = results[0]

        if result.boxes is not None:
            names = result.names
            boxes = result.boxes

            for box in boxes:
                xyxy = box.xyxy[0].tolist()
                confidence = float(box.conf[0].item())
                class_id = int(box.cls[0].item())
                class_name = names[class_id]

                row = {
                    "sequence": dataset_cfg["sequence"],
                    "frame": frame_index,
                    "image_name": image_path.name,
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "x1": float(xyxy[0]),
                    "y1": float(xyxy[1]),
                    "x2": float(xyxy[2]),
                    "y2": float(xyxy[3]),
                    "latency_ms": elapsed_ms,
                }
                rows.append(row)
                frame_detections.append(row)

        if frame_index == 0:
            first_frame_detections = frame_detections
            first_frame_image = image.copy()

    fieldnames = [
        "sequence",
        "frame",
        "image_name",
        "class_id",
        "class_name",
        "confidence",
        "x1",
        "y1",
        "x2",
        "y2",
        "latency_ms",
    ]

    with detections_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if first_frame_image is not None and first_frame_detections is not None:
        vis = draw_boxes(first_frame_image, first_frame_detections)
        cv2.imwrite(str(sample_visualization), vis)

    mean_latency = sum(frame_latencies_ms) / len(frame_latencies_ms)
    sorted_latencies = sorted(frame_latencies_ms)
    p95_index = int(round(0.95 * (len(sorted_latencies) - 1)))
    p95_latency = sorted_latencies[p95_index]
    fps = 1000.0 / mean_latency if mean_latency > 0 else 0.0

    log_text = "\n".join(
        [
            "========== M2 DETECTOR SMOKE TEST ==========",
            f"config: {args.config}",
            f"weights: {weights}",
            f"device: {device}",
            f"image_dir: {image_dir}",
            f"frames_processed: {len(image_paths)}",
            f"detections_written: {len(rows)}",
            f"detections_csv: {detections_csv}",
            f"sample_visualization: {sample_visualization}",
            f"mean_latency_ms: {mean_latency:.2f}",
            f"p95_latency_ms: {p95_latency:.2f}",
            f"fps_estimate: {fps:.2f}",
        ]
    )

    log_file.write_text(log_text + "\n", encoding="utf-8")
    print(log_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

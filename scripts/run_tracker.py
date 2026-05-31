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


def draw_track_boxes(image, detections):
    for det in detections:
        x1, y1, x2, y2 = map(int, [det["x1"], det["y1"], det["x2"], det["y2"]])
        track_id = det["track_id"]
        class_name = det["class_name"]
        conf = det["confidence"]

        label = f"ID {track_id} {class_name} {conf:.2f}"

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(
            image,
            label,
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return image


def main() -> int:
    parser = argparse.ArgumentParser(description="Run YOLOv8n + ByteTrack on KITTI frames.")
    parser.add_argument("--config", type=Path, default=Path("configs/tracker/bytetrack.yaml"))
    parser.add_argument("--max-frames", type=int, default=50)
    args = parser.parse_args()

    cfg = load_config(args.config)

    tracker_cfg = cfg["tracker"]
    dataset_cfg = cfg["dataset"]
    outputs_cfg = cfg["outputs"]
    video_cfg = cfg.get("video", {})

    weights = tracker_cfg["detector_weights"]
    tracker_config = tracker_cfg["ultralytics_tracker_config"]
    device = tracker_cfg["device"]
    imgsz = int(tracker_cfg["image_size"])
    conf = float(tracker_cfg["confidence_threshold"])
    iou = float(tracker_cfg["iou_threshold"])

    image_dir = Path(dataset_cfg["image_dir"])
    tracks_csv = Path(outputs_cfg["tracks_csv"])
    video_path = Path(outputs_cfg["video_path"])
    log_file = Path(outputs_cfg["log_file"])

    tracks_csv.parent.mkdir(parents=True, exist_ok=True)
    video_path.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(image_dir.glob("*.png"))
    if args.max_frames > 0:
        image_paths = image_paths[: args.max_frames]

    if not image_paths:
        raise FileNotFoundError(f"No PNG images found in {image_dir}")

    first_image = cv2.imread(str(image_paths[0]))
    if first_image is None:
        raise RuntimeError(f"Failed to read first image: {image_paths[0]}")

    height, width = first_image.shape[:2]
    fps = int(video_cfg.get("fps", 10))

    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError(f"Failed to open video writer: {video_path}")

    model = YOLO(weights)

    rows = []
    frame_latencies_ms = []
    unique_track_ids = set()

    for frame_index, image_path in enumerate(tqdm(image_paths, desc="Running tracker")):
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"Failed to read image: {image_path}")

        start = time.perf_counter()
        results = model.track(
            source=image,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            device=device,
            tracker=tracker_config,
            persist=True,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        frame_latencies_ms.append(elapsed_ms)

        result = results[0]
        frame_tracks = []

        if result.boxes is not None and result.boxes.id is not None:
            names = result.names

            for box in result.boxes:
                xyxy = box.xyxy[0].tolist()
                confidence = float(box.conf[0].item())
                class_id = int(box.cls[0].item())
                class_name = names[class_id]
                track_id = int(box.id[0].item())

                unique_track_ids.add(track_id)

                row = {
                    "sequence": dataset_cfg["sequence"],
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

                rows.append(row)
                frame_tracks.append(row)

        annotated = draw_track_boxes(image.copy(), frame_tracks)
        writer.write(annotated)

    writer.release()

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

    with tracks_csv.open("w", newline="", encoding="utf-8") as f:
        writer_csv = csv.DictWriter(f, fieldnames=fieldnames)
        writer_csv.writeheader()
        writer_csv.writerows(rows)

    mean_latency = sum(frame_latencies_ms) / len(frame_latencies_ms)
    sorted_latencies = sorted(frame_latencies_ms)
    p95_index = int(round(0.95 * (len(sorted_latencies) - 1)))
    p95_latency = sorted_latencies[p95_index]
    fps_estimate = 1000.0 / mean_latency if mean_latency > 0 else 0.0

    log_text = "\n".join(
        [
            "========== M3 TRACKER SMOKE TEST ==========",
            f"config: {args.config}",
            f"weights: {weights}",
            f"tracker_config: {tracker_config}",
            f"device: {device}",
            f"image_dir: {image_dir}",
            f"frames_processed: {len(image_paths)}",
            f"track_rows_written: {len(rows)}",
            f"unique_track_ids: {len(unique_track_ids)}",
            f"tracks_csv: {tracks_csv}",
            f"video_path: {video_path}",
            f"mean_latency_ms: {mean_latency:.2f}",
            f"p95_latency_ms: {p95_latency:.2f}",
            f"fps_estimate: {fps_estimate:.2f}",
        ]
    )

    log_file.write_text(log_text + "\n", encoding="utf-8")
    print(log_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Real-Time Object Tracking Under a Robotics Latency Budget

## Summary

This project builds a reproducible tracking-by-detection benchmark using a lightweight detector, ByteTrack, KITTI tracking data, tracking metrics, latency measurements, threshold sweeps, plots, and failure analysis.

## Why this project

Robot perception systems must trade off accuracy and latency. A tracker that is accurate but too slow may be unusable, while a fast tracker with many ID switches can be unreliable for deployment.

## Dataset

KITTI tracking training split with a local validation subset only. No public leaderboard submission.

## Systems compared

MVP:

- YOLOv8n detector
- ByteTrack tracker

Extensions after MVP:

- OC-SORT
- second detector
- CPU/GPU or ONNX comparison
- ROS 2 visualization
- optional C++ association module

## Pipeline

KITTI frames -> detector -> detections -> tracker -> tracks -> evaluation -> metrics.csv -> plots -> failure analysis.

## Results

Confidence threshold sweep on KITTI sequence 0000, class Car:

| conf | precision | recall | IDF1-like | MOTA-like | FP | FN | IDSW | mean ms | p95 ms |
| ---- | --------- | ------ | --------- | --------- | -- | -- | ---- | ------- | ------ |
| 0.25 | 0.294 | 0.613 | 0.310 | -0.901 | 357 | 94 | 11 | 12.34 | 15.75 |
| 0.35 | 0.319 | 0.617 | 0.359 | -0.733 | 320 | 93 | 8 | 11.74 | 12.28 |
| 0.50 | 0.386 | 0.597 | 0.430 | -0.366 | 231 | 98 | 3 | 10.90 | 12.00 |
| 0.65 | 0.472 | 0.444 | 0.441 | -0.062 | 121 | 135 | 2 | 10.67 | 11.15 |

## Accuracy-latency tradeoff

Increasing detector confidence from 0.25 to 0.65 reduced false positives from 357 to 121 and ID switches from 11 to 2, while improving local IDF1-like score from 0.310 to 0.441. The tradeoff was lower recall: 0.613 to 0.444. Plot: results/plots/m5_confidence_sweep_latency_idf1.png

## Failure analysis

Failure analysis was generated for confidence 0.65.

- False positives: 121
- False negatives / missed GT boxes: 135
- ID switches: 2
- Failure images created: 6
- Worst frames: 148, 131, 146, 147, 150, 151

Artifacts:

- reports/failure_analysis.md
- results/failure_cases/

## Reproduce

Create environment: conda create -n tracking-latency python=3.11 -y; conda activate tracking-latency; python -m pip install -r environment/requirements.txt

Core commands:

python scripts/verify_dataset.py --root data/kitti_tracking --sequences 0000 0001 --summary-csv results/tables/dataset_summary.csv

python scripts/run_detector.py --config configs/detector/yolov8n.yaml --max-frames 0

python scripts/run_tracker.py --config configs/tracker/bytetrack.yaml --max-frames 0

python scripts/evaluate_local_kitti.py --class-name Car --iou-threshold 0.5

python scripts/run_sweep.py --config configs/sweeps/confidence_sweep.yaml

python scripts/make_failure_report.py

## Tests

Tests will cover dataset parsing, detection/tracking formats, latency parsing, and result schemas.

## Limitations

Initial MVP uses pretrained detection and a small local KITTI validation split.

## Future work

OC-SORT comparison, second detector, ONNX inference, ROS 2 visualization, C++ association module, nuScenes-mini, and real camera video.

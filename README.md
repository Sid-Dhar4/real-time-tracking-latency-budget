# Real-Time Object Tracking Under a Robotics Latency Budget

[![tests](https://github.com/Sid-Dhar4/real-time-tracking-latency-budget/actions/workflows/tests.yml/badge.svg)](https://github.com/Sid-Dhar4/real-time-tracking-latency-budget/actions/workflows/tests.yml)
[![release](https://img.shields.io/badge/release-v1.1.0-blue)](docs/release_notes_v1.1.0.md)
[![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-blueviolet)](docs/ros2_replay_wrapper.md)

[![Tracking latency demo](media/tracking_latency_teaser.gif)](media/tracking_latency_demo.mp4)

Click the animation to open the full annotated demo video.

## Key results

This repository demonstrates a reproducible robotics perception benchmark for tracking-by-detection under latency and robustness constraints.

| Result area | Evidence |
| ----------- | -------- |
| Six-sequence TrackEval benchmark | HOTA `46.634`, MOTA `50.354`, IDF1 `61.903` on sequences `0000`–`0005` |
| Two-sequence TrackEval baseline | HOTA `49.412`, MOTA `52.312`, IDF1 `68.385` on sequences `0000`–`0001` |
| Tracker comparison | ByteTrack IDF1 `68.385` vs simple IoU tracker IDF1 `58.949` |
| Robustness stress test | HOTA drops from `49.412` to `25.852` when every 2nd frame is removed |
| Latency analysis | warmup-aware CPU p95 tracker latency around `16 ms` |
| Visual demo | annotated KITTI sequence `0001` overlay video |
| Failure analysis | worst-frame examples and ID-switch analysis |
| ROS 2 diagnostics latency probe | `/tracking/diagnostics` receive p95 `0.608 ms`; internal publish p95 `0.156 ms` at 10 FPS replay |
| ROS 2 debug image topic | publishes annotated KITTI frames on `/tracking/debug_image` as `sensor_msgs/Image` |
| ROS 2 workspace smoke check | builds the ROS 2 Jazzy package in a temporary colcon workspace and verifies replay executables |
| ROS 2 end-to-end topic smoke check | launches replay nodes and verifies `/tracking/status`, `/tracking/objects`, `/tracking/detections_2d`, `/tracking/diagnostics`, and `/tracking/debug_image` publish |
| Track reliability risk diagnostics | deterministic risk ranking for low-confidence, short-lived, border-adjacent, or jumpy tracks |
| Risk-score validation | high/medium risk buckets have shorter lifetimes and lower confidence than low-risk tracks |
| Risk vs failure correlation | risk aligns with track fragmentation and frame-level FP/FN burden; ID switches remain a separate long-track failure mode |
| Runtime environment audit | documents CPU/GPU runtime state and CUDA-enabled PyTorch availability |
| CPU/GPU latency benchmark | measured YOLOv8n inference: CPU 9.40 ms mean, GPU 3.22 ms mean, 2.92x GPU speedup |

Core artifacts:

- `reports/trackeval_results.md`
- `reports/trackeval_stress_test.md`
- `reports/tracker_comparison.md`
- `reports/runtime_analysis.md`
- `reports/track_reliability_risk.md`
- `reports/track_risk_validation.md`
- `reports/risk_failure_correlation.md`
- `reports/runtime_environment_audit.md`
- `reports/cpu_gpu_latency_benchmark.md`
- `docs/reproduction_matrix.md`
- `docs/reviewer_proof_pack.md`
- `docs/release_notes_v1.1.0.md`
- `results/videos/m11_seq0001_demo_overlay.mp4`

## Visual artifacts

| Artifact | Path |
| -------- | ---- |
| Clickable README teaser GIF | `media/tracking_latency_teaser.gif` |
| Full annotated demo video | `media/tracking_latency_demo.mp4` |
| Demo poster frame | `media/tracking_latency_poster.jpg` |
| ROS 2 debug image sample | `media/tracking_debug_image_sample.jpg` |
| Latency distribution plot | `results/plots/m12_latency_histogram.png` |
| Dropped-frame stress plot | `results/plots/m14_trackeval_stress_metrics.png` |
| Tracker comparison plot | `results/plots/m15_tracker_comparison_metrics.png` |
| Six-sequence TrackEval plot | `results/plots/m21_trackeval_6seq_metrics.png` |

## Summary

This project builds a reproducible tracking-by-detection benchmark using a lightweight detector, ByteTrack, KITTI tracking data, tracking metrics, latency measurements, threshold sweeps, plots, and failure analysis.

## Why this project

Robot perception systems must trade off accuracy and latency. A tracker that is accurate but too slow may be unusable, while a fast tracker with many ID switches can be unreliable for deployment.

## ROS 2 replay wrapper

A ROS 2 Jazzy wrapper replays saved KITTI tracking outputs and publishes JSON compatibility topics, typed robotics-native tracking outputs, diagnostics, latency-probe support, and annotated debug images: `/tracking/objects`, `/tracking/status`, `/tracking/detections_2d`, `/tracking/diagnostics`, and `/tracking/debug_image`.

Documentation: `docs/ros2_replay_wrapper.md` and `ros2/ros2_tracking_latency`.

## Release

Current release: `v1.1.0`

- Release notes: `docs/release_notes_v1.1.0.md`
- Tag: `v1.1.0`
- Scope: v1.0.0 benchmark baseline plus track reliability diagnostics, risk validation, CPU/GPU latency benchmark, CUDA runtime audit, ROS 2 workspace smoke check, ROS 2 end-to-end topic smoke check, reproduction matrix, and reviewer proof pack.
- Prior baseline: `docs/release_notes_v1.0.0.md`

## Reproducibility checks

This repository includes local tests and CI checks for schemas, KITTI label sanity, IoU tracker behavior, benchmark artifacts, metric regressions, and stale README claims:

```bash
bash scripts/run_tests.sh
python scripts/check_artifacts_exist.py

# Optional local ROS 2 Jazzy smoke check
bash scripts/check_ros2_workspace.sh

# Optional local ROS 2 end-to-end topic smoke check
bash scripts/check_ros2_end_to_end_topics.sh
```

GitHub Actions runs these checks on push and pull request via `.github/workflows/tests.yml`.

## Reproduction matrix

For fast auditing, see `docs/reproduction_matrix.md`. It maps each headline claim to the command, expected result, and checked-in evidence.

## Reviewer proof pack

For the fastest audit path, see `docs/reviewer_proof_pack.md`. It summarizes the strongest evidence, claim boundaries, and recommended inspection order.

## Environment setup

Recommended setup:

```bash
conda create -n tracking-latency python=3.11 -y
conda activate tracking-latency
python -m pip install -r environment/requirements-dev.txt
```

Environment files:

- `environment/requirements-minimal.txt`: runtime dependencies for benchmark scripts.
- `environment/requirements-dev.txt`: runtime dependencies plus test tooling.
- `environment/environment-lock-full.txt`: archived local full freeze, not the recommended install path.

## Dataset

KITTI tracking training split with a local validation subset only. No public leaderboard submission.

## Systems compared

Implemented:

- YOLOv8n detector
- ByteTrack tracker
- Simple IoU tracker baseline
- ROS 2 replay wrapper with JSON compatibility topics, typed `vision_msgs/Detection2DArray` outputs, `diagnostic_msgs/DiagnosticArray` diagnostics, a diagnostics latency probe, and `/tracking/debug_image`

Future optional extensions:

- OC-SORT or second detector comparison
- ONNX/TensorRT export or an online ROS 2 detector node
- C++ association module

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

## Local diagnostic benchmark on sequences 0000–0001

This earlier local diagnostic table uses KITTI sequences `0000` and `0001` for class `Car`. The primary benchmark is the six-sequence native TrackEval section.

| sequence | GT | predictions | TP | FP | FN | IDSW | precision | recall | MOTA-like | IDF1-like |
| -------- | -- | ----------- | -- | -- | -- | ---- | --------- | ------ | --------- | --------- |
| 0000 | 243 | 506 | 149 | 357 | 94 | 11 | 0.294 | 0.613 | -0.901 | 0.310 |
| 0001 | 2681 | 2300 | 1756 | 544 | 925 | 49 | 0.763 | 0.655 | 0.434 | 0.647 |

This matters because sequence `0001` is longer and has many more ground-truth car instances, making the project less dependent on one short clip.
## Demo video

Annotated demo artifacts are included for KITTI sequence `0001`:

- Video: `results/videos/m11_seq0001_demo_overlay.mp4`
- Sample frame: `results/plots/m11_seq0001_demo_frame.jpg`
- Notes: `reports/demo_notes.md`

The overlay shows track boxes, track IDs, class names, confidence scores, frame number, and per-frame tracker latency.

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

Create environment: conda create -n tracking-latency python=3.11 -y; conda activate tracking-latency; python -m pip install -r environment/requirements-dev.txt

Core commands:

python scripts/verify_dataset.py --root data/kitti_tracking --sequences 0000 0001 --summary-csv results/tables/dataset_summary.csv

python scripts/run_detector.py --config configs/detector/yolov8n.yaml --max-frames 0

python scripts/run_tracker.py --config configs/tracker/bytetrack.yaml --max-frames 0

python scripts/evaluate_local_kitti.py --class-name Car --iou-threshold 0.5

python scripts/run_sweep.py --config configs/sweeps/confidence_sweep.yaml

python scripts/make_failure_report.py

## Tests

Tests cover result schemas, tracked benchmark artifacts, and KITTI label-format sanity checks via `scripts/run_tests.sh`.

## Six-sequence TrackEval benchmark

The benchmark was expanded from two KITTI tracking sequences to six sequences: `0000`–`0005`.

Combined native TrackEval KITTI results for ByteTrack on class `car`:

- HOTA: `46.634`
- MOTA: `50.354`
- IDF1: `61.903`
- GT detections: `5793`
- Tracker detections: `3780`
- ID switches: `121`

Artifacts:

- `reports/trackeval_6seq_results.md`
- `results/tables/m21_trackeval_6seq_summary.csv`
- `results/plots/m21_trackeval_6seq_metrics.png`
- `results/trackeval_6seq/m21_car_summary.txt`

## TrackEval KITTI metrics

Native TrackEval KITTI 2D box evaluation was run for class `car` on KITTI tracking sequences `0000` and `0001`.

Combined results:

- HOTA: `49.412`
- MOTA: `52.312`
- IDF1: `68.385`

Per-sequence highlights:

| sequence | HOTA | MOTA | IDF1 |
| -------- | ---- | ---- | ---- |
| 0000 | 43.489 | 25.581 | 51.084 |
| 0001 | 50.009 | 54.842 | 70.177 |

Artifacts:

- `reports/trackeval_results.md`
- `results/trackeval/m13_car_summary.txt`
- `results/trackeval/m13_car_detailed.csv`

These are TrackEval metrics, not a public KITTI leaderboard submission.

## Dropped-frame robustness stress test

A TrackEval stress test was added by removing tracker outputs from every Nth frame before evaluation.

Combined TrackEval results:

| variant | HOTA | MOTA | IDF1 |
| ------- | ---- | ---- | ---- |
| baseline | 49.412 | 52.312 | 68.385 |
| drop every 5th frame | 39.974 | 41.496 | 59.737 |
| drop every 3rd frame | 33.765 | 34.700 | 53.454 |
| drop every 2nd frame | 25.852 | 25.613 | 43.846 |

Artifacts:

- `reports/trackeval_stress_test.md`
- `results/tables/m14_trackeval_stress_summary.csv`
- `results/plots/m14_trackeval_stress_metrics.png`

This demonstrates sensitivity to intermittent detector/tracker output under simulated dropped-frame perception failures.

## Tracker comparison baseline

A simple IoU tracker baseline was added and compared against ByteTrack using the same YOLOv8n detections and native TrackEval KITTI evaluation.

Combined TrackEval results:

| tracker | HOTA | MOTA | IDF1 | IDSW | FP | FN | IDs |
| ------- | ---- | ---- | ---- | ---- | -- | -- | --- |
| ByteTrack | 49.412 | 52.312 | 68.385 | 42 | 296 | 848 | 135 |
| Simple IoU tracker | 48.814 | 45.879 | 58.949 | 197 | 705 | 444 | 436 |

The IoU tracker keeps more detections and achieves higher recall, but creates far more ID switches and fragmented identities. ByteTrack is stronger for identity consistency and overall tracking quality.

Artifacts:

- `reports/tracker_comparison.md`
- `results/tables/m15_tracker_comparison.csv`
- `results/plots/m15_tracker_comparison_metrics.png`

## Runtime analysis

Warmup-aware CPU tracker latency plots are included:

- Histogram: `results/plots/m12_latency_histogram.png`
- Summary bar plot: `results/plots/m12_latency_summary_bar.png`
- Report: `reports/runtime_analysis.md`

The first 5 frames are excluded as warmup. Detector-only CPU/GPU latency is reported separately in `reports/cpu_gpu_latency_benchmark.md`.

## Limitations

The detector uses pretrained YOLOv8n weights, not KITTI-specific training. Results are local reproducible evaluations on KITTI training sequences, not a public KITTI leaderboard submission. The ROS 2 package is currently a replay wrapper over saved tracking outputs, not an online detector/tracker node.

## Future work

OC-SORT or BoT-SORT comparison, ONNX/TensorRT export, C++ association/risk core, online ROS 2 detector/tracker node, nuScenes-mini, and real camera video.

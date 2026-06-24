# Reviewer Proof Pack

This is the fastest path for a recruiter, hiring manager, or robotics perception interviewer to evaluate the project.

## One-sentence summary

This repository is a reproducible robotics perception benchmark for tracking-by-detection under latency, robustness, ROS 2 deployment, and reliability-diagnostic constraints.

## What to inspect first

| Order | What to inspect | Why it matters |
| ----- | --------------- | -------------- |
| 1 | README key-results table | high-level evidence in one screen |
| 2 | `docs/reproduction_matrix.md` | maps claims to commands and artifacts |
| 3 | `reports/cpu_gpu_latency_benchmark.md` | measured CPU vs GPU detector latency |
| 4 | `reports/trackeval_6seq_results.md` | multi-sequence tracking metrics |
| 5 | `reports/trackeval_stress_test.md` | robustness under dropped-frame stress |
| 6 | `reports/track_reliability_risk.md` and `reports/track_risk_validation.md` | deterministic track-risk diagnostics and validation |
| 7 | `reports/ros2_end_to_end_topic_smoke_check.md` | ROS 2 nodes actually publish expected topics |
| 8 | `media/tracking_latency_demo.mp4` | visual tracking demo |

## Strongest evidence

### 1. Tracking benchmark

The project evaluates YOLOv8n + ByteTrack on KITTI tracking sequences and reports TrackEval metrics, including HOTA, MOTA, and IDF1.

Evidence:

- `reports/trackeval_6seq_results.md`
- `results/plots/m21_trackeval_6seq_metrics.png`

### 2. Robustness stress test

The project simulates dropped-frame stress and measures metric degradation.

Evidence:

- `reports/trackeval_stress_test.md`
- `results/plots/m14_trackeval_stress_metrics.png`

### 3. Tracker comparison baseline

ByteTrack is compared against a simple IoU tracker baseline using the same detections and evaluation path.

Evidence:

- `reports/tracker_comparison.md`
- `results/plots/m15_tracker_comparison_metrics.png`

### 4. CPU/GPU latency benchmark

The project measures YOLOv8n detector inference latency on CPU and GPU.

Measured result:

- CPU mean latency: about 9.40 ms
- GPU mean latency: about 3.22 ms
- GPU mean-latency speedup: about 2.92x
- Both CPU and GPU meet 30 Hz and 60 Hz detector-only latency budgets in the measured benchmark.

Evidence:

- `reports/cpu_gpu_latency_benchmark.md`
- `results/tables/m36_cpu_gpu_latency_summary.csv`
- `results/plots/m36_cpu_gpu_latency_comparison.png`

### 5. Track reliability risk diagnostics

The project adds deterministic risk scoring for unstable tracks using low confidence, small boxes, border proximity, motion jumps, and short track duration.

Evidence:

- `scripts/compute_track_risk.py`
- `reports/track_reliability_risk.md`
- `reports/track_risk_validation.md`
- `results/tables/m33_track_risk_summary.csv`
- `results/tables/m34_risk_bucket_summary.csv`

### 6. ROS 2 replay wrapper

The project includes a ROS 2 Jazzy package that replays saved tracking outputs into robotics-style topics.

Verified topics:

- `/tracking/status`
- `/tracking/objects`
- `/tracking/detections_2d`
- `/tracking/diagnostics`
- `/tracking/debug_image`

Evidence:

- `docs/ros2_replay_wrapper.md`
- `reports/ros2_workspace_smoke_check.md`
- `reports/ros2_end_to_end_topic_smoke_check.md`
- `scripts/check_ros2_workspace.sh`
- `scripts/check_ros2_end_to_end_topics.sh`

### 7. Reproducibility and CI

The project includes local tests, artifact checks, and GitHub Actions.

Evidence:

- `.github/workflows/tests.yml`
- `scripts/run_tests.sh`
- `scripts/check_artifacts_exist.py`
- `docs/reproduction_matrix.md`

## Claim boundaries

This repository reports local reproducible benchmark results, not a public KITTI leaderboard submission.

The CPU/GPU latency benchmark measures detector inference on preloaded KITTI frames. It does not include full robot system latency, camera transport, planner latency, or actuation.

The ROS 2 end-to-end check is a smoke test. It proves the replay nodes build, launch, publish, and can be observed through ROS 2 topics on a local ROS 2 Jazzy installation.

The track risk score is a deterministic diagnostic heuristic, not a learned uncertainty model or safety certification metric.

## Interview explanation

A concise way to explain the project:

    I built a reproducible robotics perception benchmark around YOLOv8n and ByteTrack on KITTI tracking data. The project evaluates accuracy with TrackEval, latency with CPU/GPU benchmarks, robustness with dropped-frame stress tests, and deployment behavior with a ROS 2 Jazzy replay wrapper. I also added deterministic track-risk diagnostics to identify unstable tracks and validated that higher-risk buckets correspond to shorter-lived and lower-confidence tracks. The repo includes tests, CI, reproduction docs, reports, plots, videos, and ROS 2 smoke checks.

## Resume-level claim

    Built a reproducible robotics perception benchmark for YOLOv8n + ByteTrack on KITTI, combining TrackEval metrics, dropped-frame robustness stress tests, CPU/GPU latency benchmarking, deterministic track-risk diagnostics, and a ROS 2 Jazzy replay wrapper with end-to-end topic smoke checks.

## Recommended reviewer command sequence

Run basic checks:

    bash scripts/run_tests.sh
    python scripts/check_artifacts_exist.py

Run ROS 2 build smoke check, if ROS 2 Jazzy is installed:

    bash scripts/check_ros2_workspace.sh

Run ROS 2 end-to-end topic smoke check, if ROS 2 Jazzy and local KITTI artifacts are available:

    bash scripts/check_ros2_end_to_end_topics.sh

Run CPU/GPU latency benchmark, if CUDA PyTorch is available:

    python scripts/benchmark_cpu_gpu_latency.py --config configs/detector/yolov8n.yaml --max-frames 100 --warmup-frames 5 --raw-output results/tables/m36_cpu_gpu_latency_raw.csv --summary-output results/tables/m36_cpu_gpu_latency_summary.csv --plot-output results/plots/m36_cpu_gpu_latency_comparison.png

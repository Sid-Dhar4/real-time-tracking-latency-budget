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
| 7 | `reports/ros2_end_to_end_topic_smoke_check.md` | ROS 2 replay nodes publish expected topics |
| 8 | `reports/cpp_tracking_core.md` | C++ association, track lifecycle, risk scoring, tests, and microbenchmark |
| 9 | `reports/online_ros_image_tracking.md` | online ROS 2 image callback node publishes tracking/risk/safety topics |
| 10 | `media/tracking_latency_demo.mp4` | visual tracking demo |

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

The risk/failure correlation report shows that risk aligns with track fragmentation and frame-level FP/FN burden, while ID switches remain a separate long-track identity-consistency failure mode.

Evidence:

- `scripts/compute_track_risk.py`
- `reports/track_reliability_risk.md`
- `reports/track_risk_validation.md`
- `reports/risk_failure_correlation.md`
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
- `/tracking/risk`
- `/tracking/safety_status`

Evidence:

- `docs/ros2_replay_wrapper.md`
- `reports/ros2_workspace_smoke_check.md`
- `reports/ros2_end_to_end_topic_smoke_check.md`
- `reports/robot_facing_risk_interface.md`
- `scripts/check_ros2_workspace.sh`
- `scripts/check_ros2_end_to_end_topics.sh`

### 7. Reproducibility and CI

The project includes local tests, artifact checks, and GitHub Actions.

Evidence:

- `.github/workflows/tests.yml`
- `scripts/run_tests.sh`
- `scripts/check_artifacts_exist.py`
- `docs/reproduction_matrix.md`


### 8. C++ tracking core

The project includes a compact C++ module for latency-critical tracking primitives: IoU association, track lifecycle state, risk scoring, tests, and a microbenchmark.

Evidence:

- `cpp/tracking_core/`
- `scripts/check_cpp_tracking_core.sh`
- `reports/cpp_tracking_core.md`


### 9. Online ROS 2 image tracking node

The project includes an online callback-driven ROS 2 node that subscribes to `/camera/image_raw` and publishes tracking, typed detection, diagnostic, risk, and safety-status topics.

Evidence:

- `ros2/ros2_tracking_latency/ros2_tracking_latency/image_iou_tracking_node.py`
- `scripts/check_ros2_online_image_tracking.sh`
- `reports/online_ros_image_tracking.md`

## Claim boundaries

This repository reports local reproducible benchmark results, not a public KITTI leaderboard submission.

The CPU/GPU latency benchmark measures detector inference on preloaded KITTI frames. It does not include full robot system latency, camera transport, planner latency, or actuation.

The ROS 2 end-to-end check is a smoke test. It proves the replay nodes build, launch, publish, and can be observed through ROS 2 topics on a local ROS 2 Jazzy installation.

The track risk score is a deterministic diagnostic heuristic, not a learned uncertainty model or safety certification metric.

## Interview explanation

A concise way to explain the project:

    I built a reproducible robotics perception benchmark around YOLOv8n and ByteTrack on KITTI tracking data. The project evaluates accuracy with native TrackEval metrics, latency with CPU/GPU benchmarks, robustness with dropped-frame stress tests, and deployment behavior with ROS 2 Jazzy replay and online image-tracking smoke checks. I added deterministic track-risk diagnostics, validated them against fragmentation and frame-level FP/FN burden, exposed robot-facing `/tracking/risk` and `/tracking/safety_status` topics, and implemented a compact C++ tracking core for IoU association, track lifecycle, risk scoring, tests, and microbenchmarking.

## Resume-level claim

    Built a reproducible robotics perception benchmark for YOLOv8n + ByteTrack on KITTI, combining TrackEval HOTA/MOTA/IDF1 metrics, dropped-frame robustness tests, CPU/GPU latency benchmarking, deterministic track-risk diagnostics, ROS 2 Jazzy replay and online image-tracking smoke checks, robot-facing risk/safety topics, and a C++ tracking core with tests and microbenchmark.

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


Run online ROS 2 image tracking smoke check, if ROS 2 Jazzy is installed:

    bash scripts/check_ros2_online_image_tracking.sh

# Reproduction Matrix

This document maps the repository's main claims to the command, expected output, and checked-in evidence.

The goal is to make the project easy to audit quickly without reading every script first.

## Quick verification

| Claim | Command | Expected result | Evidence |
| ----- | ------- | --------------- | -------- |
| Unit tests and artifact checks pass | `bash scripts/run_tests.sh` and `python scripts/check_artifacts_exist.py` | all tests pass and required artifacts exist | `.github/workflows/tests.yml` |
| CPU/GPU runtime is available | inspect `reports/runtime_environment_audit.md` | CUDA-enabled PyTorch available in `tracking-latency` | `results/tables/m35_runtime_environment_audit.csv` |
| CPU/GPU detector latency is measured | `python scripts/benchmark_cpu_gpu_latency.py --config configs/detector/yolov8n.yaml --max-frames 100 --warmup-frames 5 --raw-output results/tables/m36_cpu_gpu_latency_raw.csv --summary-output results/tables/m36_cpu_gpu_latency_summary.csv --plot-output results/plots/m36_cpu_gpu_latency_comparison.png` | CPU mean about 9.40 ms, GPU mean about 3.22 ms, GPU speedup about 2.92x | `reports/cpu_gpu_latency_benchmark.md` |
| Six-sequence TrackEval benchmark exists | inspect TrackEval report and summary table | HOTA/MOTA/IDF1 reported for KITTI sequences 0000-0005 | `reports/trackeval_6seq_results.md` |
| Dropped-frame robustness stress test exists | inspect stress report and plot | metrics drop under simulated frame loss | `reports/trackeval_stress_test.md` |
| ByteTrack beats simple IoU tracker baseline | inspect tracker comparison report | ByteTrack has higher IDF1 than IoU baseline | `reports/tracker_comparison.md` |
| Track reliability risk diagnostics exist | `python scripts/compute_track_risk.py` | risky tracks ranked by confidence, size, border proximity, jumps, and duration | `reports/track_reliability_risk.md` |
| Risk-score validation exists | inspect risk validation report | high/medium risk buckets are shorter-lived and lower-confidence than low-risk tracks | `reports/track_risk_validation.md` |
| Risk/failure correlation exists | `python scripts/analyze_risk_failure_correlation.py` | risk aligns with fragmentation and frame-level FP/FN burden; ID switches are documented as a separate failure mode | `reports/risk_failure_correlation.md` |
| ROS 2 typed replay wrapper exists | inspect ROS 2 wrapper docs | JSON compatibility topics, typed detections, diagnostics, and debug images documented | `docs/ros2_replay_wrapper.md` |
| ROS 2 workspace smoke check passes | `bash scripts/check_ros2_workspace.sh` | package builds in a temporary colcon workspace and replay executables are discoverable | `reports/ros2_workspace_smoke_check.md` |
| ROS 2 end-to-end topics publish | `bash scripts/check_ros2_end_to_end_topics.sh` | replay nodes publish status, objects, typed detections, diagnostics, and debug image topics | `reports/ros2_end_to_end_topic_smoke_check.md` |
| Robot-facing risk/safety topics publish | `bash scripts/check_ros2_end_to_end_topics.sh` | `/tracking/risk` and `/tracking/safety_status` publish with risk summary and safety state | `reports/robot_facing_risk_interface.md` |
| ROS 2 diagnostic latency probe exists | inspect latency probe report | diagnostics receive p95 and internal publish p95 reported | `reports/ros2_latency_probe.md` |
| Demo video exists | inspect visual artifacts | annotated KITTI tracking overlay video and teaser GIF exist | `media/tracking_latency_teaser.gif`, `media/tracking_latency_demo.mp4` |

## Recommended audit order

1. Read `docs/reviewer_proof_pack.md`.
2. Read the README key-results table.
3. Run the tests and artifact checker.
4. Inspect `reports/cpu_gpu_latency_benchmark.md`.
5. Inspect `reports/trackeval_6seq_results.md`.
6. Inspect `reports/track_reliability_risk.md` and `reports/track_risk_validation.md`.
7. Inspect `docs/ros2_replay_wrapper.md`.
8. Watch `media/tracking_latency_demo.mp4`.

## Claim boundaries

This project reports local reproducible benchmark results, not a public KITTI leaderboard submission.

The CPU/GPU benchmark measures detector inference on preloaded KITTI frames. It does not include full robot system latency, camera transport, ROS 2 message passing, planner latency, or actuation.

The risk score is a deterministic diagnostic heuristic. It is not a learned uncertainty model or safety certification metric.

## Core commands

Create and activate the environment:

    conda create -n tracking-latency python=3.11 -y
    conda activate tracking-latency
    python -m pip install -r environment/requirements-dev.txt

Run checks:

    bash scripts/run_tests.sh
    python scripts/check_artifacts_exist.py

Run CPU/GPU latency benchmark:

    python scripts/benchmark_cpu_gpu_latency.py --config configs/detector/yolov8n.yaml --max-frames 100 --warmup-frames 5 --raw-output results/tables/m36_cpu_gpu_latency_raw.csv --summary-output results/tables/m36_cpu_gpu_latency_summary.csv --plot-output results/plots/m36_cpu_gpu_latency_comparison.png

Run track risk diagnostics:

    python scripts/compute_track_risk.py --tracks-csv results/tracks/yolov8n_bytetrack_seq0001_tracks.csv --frame-output results/tables/m33_frame_risk_scores.csv --track-output results/tables/m33_track_risk_summary.csv --top-k-output results/tables/m33_top_risky_tracks.csv --top-k 20

Run ROS 2 workspace smoke check:

    bash scripts/check_ros2_workspace.sh

Run ROS 2 end-to-end topic smoke check:

    bash scripts/check_ros2_end_to_end_topics.sh

Run risk-vs-failure correlation:

    python scripts/analyze_risk_failure_correlation.py

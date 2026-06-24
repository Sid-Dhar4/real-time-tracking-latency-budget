# Release v1.1.0

This release upgrades the tracking latency benchmark from the original v1.0.0 baseline into a stronger robotics perception systems artifact.

## Summary

v1.1.0 adds risk diagnostics, CPU/GPU latency benchmarking, CUDA runtime auditing, ROS 2 workspace checks, ROS 2 end-to-end topic checks, a reproduction matrix, and a reviewer proof pack.

## Major additions since v1.0.0

### Track reliability diagnostics

Added deterministic track-level risk scoring for unstable tracks using:

- low confidence
- small projected box size
- image-border proximity
- motion jumps
- short track duration

Evidence:

- `scripts/compute_track_risk.py`
- `reports/track_reliability_risk.md`
- `reports/track_risk_validation.md`
- `results/tables/m33_track_risk_summary.csv`
- `results/tables/m34_risk_bucket_summary.csv`

### Risk-score validation

Added a validation report showing that higher-risk buckets correspond to shorter-lived and lower-confidence tracks.

Evidence:

- `reports/track_risk_validation.md`
- `results/tables/m34_risk_bucket_summary.csv`
- `results/plots/m34_risk_bucket_summary.png`

### CPU/GPU latency benchmark

Added a measured CPU-vs-GPU YOLOv8n detector latency benchmark after enabling CUDA PyTorch in the project environment.

Measured result:

- CPU mean latency: about 9.40 ms
- GPU mean latency: about 3.22 ms
- GPU mean-latency speedup: about 2.92x
- CPU p95 latency: about 9.87 ms
- GPU p95 latency: about 3.25 ms
- Both CPU and GPU meet 30 Hz and 60 Hz detector-only latency budgets in the measured benchmark.

Evidence:

- `scripts/benchmark_cpu_gpu_latency.py`
- `reports/cpu_gpu_latency_benchmark.md`
- `results/tables/m36_cpu_gpu_latency_summary.csv`
- `results/plots/m36_cpu_gpu_latency_comparison.png`

### Runtime environment audit

Added runtime environment documentation for CPU/GPU state, NVIDIA driver, CUDA-enabled PyTorch, and benchmark claim boundaries.

Evidence:

- `reports/runtime_environment_audit.md`
- `results/tables/m35_runtime_environment_audit.csv`

### ROS 2 workspace smoke check

Added a local ROS 2 Jazzy workspace smoke check that builds the package in a temporary colcon workspace and verifies replay executables.

Evidence:

- `scripts/check_ros2_workspace.sh`
- `reports/ros2_workspace_smoke_check.md`

### ROS 2 end-to-end topic smoke check

Added an end-to-end ROS 2 smoke check that launches replay nodes and verifies expected topics publish.

Verified topics:

- `/tracking/status`
- `/tracking/objects`
- `/tracking/detections_2d`
- `/tracking/diagnostics`
- `/tracking/debug_image`

Evidence:

- `scripts/check_ros2_end_to_end_topics.sh`
- `reports/ros2_end_to_end_topic_smoke_check.md`

### Reproduction and reviewer documentation

Added documentation that maps claims to commands, evidence, and inspection order.

Evidence:

- `docs/reproduction_matrix.md`
- `docs/reviewer_proof_pack.md`

## Existing v1.0.0 baseline retained

v1.1.0 keeps the original v1.0.0 benchmark foundation:

- six-sequence TrackEval benchmark
- dropped-frame robustness stress test
- ByteTrack vs simple IoU tracker comparison
- latency analysis
- failure analysis
- visual tracking demo
- ROS 2 replay wrapper

## Validation

Before release, the following checks passed:

- local unit tests
- artifact and stale-claim checker
- GitHub Actions workflow
- local ROS 2 workspace smoke check
- local ROS 2 end-to-end topic smoke check

## Claim boundaries

This release reports local reproducible benchmark results, not a public KITTI test-server or leaderboard submission.

The CPU/GPU latency benchmark measures detector inference on preloaded KITTI frames. It does not include full robot system latency, camera transport, ROS 2 message passing, planner latency, or actuation.

The ROS 2 checks are smoke tests. They verify build, launch, topic publication, and topic observation on a local ROS 2 Jazzy installation.

The track risk score is a deterministic diagnostic heuristic, not a learned uncertainty model or safety certification metric.

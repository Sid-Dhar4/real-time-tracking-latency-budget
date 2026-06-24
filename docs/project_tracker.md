# Project Tracker — Real-Time Object Tracking Under a Robotics Latency Budget

This file is the final recruiter-facing tracker. Earlier block-by-block development logs were consolidated to remove stale milestone language.

## Current status

| Area | Status |
| ---- | ------ |
| Benchmark pipeline | complete |
| Six-sequence TrackEval evaluation | complete |
| Robustness stress test | complete |
| Tracker comparison | complete |
| CPU/GPU latency benchmark | complete |
| Track reliability risk diagnostics | complete |
| Risk-vs-failure correlation | complete |
| ROS 2 replay wrapper | complete |
| Robot-facing risk/safety topics | complete |
| C++ tracking core | complete |
| Online ROS 2 image tracking smoke-test node | complete |
| v1.2.0 release packaging | in progress |

## Final milestone summary

| Milestone | Result | Evidence |
| --------- | ------ | -------- |
| Dataset + pipeline | KITTI tracking data prepared, YOLOv8n detections, ByteTrack tracks | `results/tables/dataset_summary.csv`, `results/tracks/` |
| Evaluation | Native TrackEval KITTI evaluation on sequences `0000`–`0005` | `reports/trackeval_6seq_results.md` |
| Robustness | Dropped-frame stress testing | `reports/trackeval_stress_test.md` |
| Baseline comparison | ByteTrack compared against simple IoU tracker | `reports/tracker_comparison.md` |
| Latency | CPU tracker latency and CPU/GPU detector latency measured | `reports/runtime_analysis.md`, `reports/cpu_gpu_latency_benchmark.md` |
| Risk diagnostics | Per-track risk scoring and validation | `reports/track_reliability_risk.md`, `reports/track_risk_validation.md` |
| Risk/failure correlation | Risk aligned with fragmentation and frame-level FP/FN burden | `reports/risk_failure_correlation.md` |
| ROS 2 replay | Replay wrapper publishes tracking, typed detections, diagnostics, debug images, risk, and safety status | `docs/ros2_replay_wrapper.md` |
| C++ core | IoU association, track lifecycle, risk scoring, tests, and microbenchmark | `reports/cpp_tracking_core.md` |
| Online ROS 2 node | `image_iou_tracking` subscribes to `/camera/image_raw` and publishes tracking/risk/safety topics | `reports/online_ros_image_tracking.md` |
| Reproducibility | Tests, CI, artifact checker, reproduction matrix, reviewer proof pack | `.github/workflows/tests.yml`, `docs/reproduction_matrix.md`, `docs/reviewer_proof_pack.md` |

## Claim boundaries

- Results are local reproducible evaluations, not a public KITTI leaderboard submission.
- The online ROS 2 image node is a smoke-testable architecture demo using deterministic bright-region detection; benchmark results remain based on YOLOv8n + ByteTrack.
- The CPU/GPU benchmark measures detector inference, not full robot system latency.
- The risk score is a deterministic diagnostic heuristic, not certified safety logic.

## Remaining optional future work

- OC-SORT or BoT-SORT comparison.
- ONNX/TensorRT export.
- Real camera video integration.
- Additional dataset such as nuScenes-mini.
- Public benchmark submission.

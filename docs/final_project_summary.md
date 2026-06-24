# Final Project Summary

## Project

Real-Time Object Tracking Under a Robotics Latency Budget

## One-line description

A reproducible robotics perception benchmark that evaluates YOLOv8n + ByteTrack object tracking on KITTI sequences with latency profiling, TrackEval metrics, failure analysis, robustness stress tests, ROS 2 replay/online smoke checks, risk diagnostics, and a C++ tracking core.

## What was built

- KITTI tracking benchmark pipeline for sequences `0000`–`0005`
- YOLOv8n detector outputs
- ByteTrack tracker outputs
- Local KITTI-style evaluator
- Native TrackEval KITTI evaluation
- Confidence-threshold sweep
- Warmup-aware CPU latency summaries and plots
- Annotated demo video
- Dropped-frame robustness stress test
- Simple IoU tracker baseline for algorithm comparison
- Tests for schema and dataset sanity
- ROS 2 diagnostics latency probe for typed replay topics
- ROS 2 debug image replay topic for annotated KITTI tracking frames
- Track reliability risk diagnostics for unstable tracks
- Risk-score validation showing high/medium risk buckets are shorter-lived and lower-confidence
- Runtime environment audit documenting CPU benchmark support and CUDA-enabled PyTorch availability
- CPU/GPU latency benchmark measuring YOLOv8n inference on RTX 5060 Laptop GPU
- Reproduction matrix mapping headline claims to commands, expected outputs, and artifacts
- ROS 2 workspace smoke check builds the package in a temporary colcon workspace and verifies replay executables
- ROS 2 end-to-end topic smoke check verifies replay nodes publish status, objects, typed detections, diagnostics, and debug images
- Reviewer proof pack summarizing strongest evidence, claim boundaries, and inspection order
- Risk-vs-failure correlation showing risk aligns with track fragmentation and frame-level FP/FN burden while ID switches remain a separate identity-consistency failure mode
- Robot-facing ROS 2 risk/safety topics expose per-frame reliability summaries as `/tracking/risk` and `/tracking/safety_status`
- C++ tracking core implements IoU association, track lifecycle, risk scoring, tests, and a microbenchmark
- Online ROS 2 image tracking node subscribes to `/camera/image_raw` and publishes tracking, detection, risk, and safety-status topics

## Strongest measured results

- Six-sequence ByteTrack native TrackEval combined results: HOTA `46.634`, MOTA `50.354`, IDF1 `61.903` across `5,793` ground-truth detections
- Two-sequence controlled tracker comparison: ByteTrack IDF1 `68.385` vs simple IoU tracker IDF1 `58.949`
- ByteTrack vs simple IoU tracker: ID switches `42` vs `197`
- Dropped-frame stress test: HOTA degrades from `49.412` baseline to `25.852` when every 2nd frame is removed
- Warmup-aware CPU tracker p95 latency is approximately `16 ms` on both evaluated sequences
- ROS 2 diagnostics latency probe: receive p95 `0.608 ms`, internal publish p95 `0.156 ms` at 10 FPS replay
- ROS 2 debug image topic publishes annotated `sensor_msgs/Image` frames with track boxes and IDs
- Track reliability risk diagnostics rank unstable tracks using confidence, box size, border proximity, motion jumps, and track length
- Risk-score validation shows high-risk track lifetime `1.0` frame vs low-risk average `18.9` frames, with lower mean confidence
- CPU/GPU benchmark measured 9.40 ms CPU mean latency vs 3.22 ms GPU mean latency, a 2.92x mean-latency speedup

## Honest caveats

- This is not a public KITTI leaderboard submission.
- The detector is pretrained YOLOv8n, not trained from scratch or fine-tuned on KITTI.
- The online ROS 2 image node uses a deterministic bright-region detector for smoke-testable architecture validation; the measured benchmark results still come from YOLOv8n + ByteTrack outputs.
- The CPU/GPU latency benchmark measures detector inference on preloaded frames, not full robot latency including camera transport, planning, or actuation.
- The track-risk score is a deterministic diagnostic heuristic, not a learned uncertainty model or certified safety metric.
- The project focuses on tracking-by-detection benchmarking and robotics perception infrastructure, not full autonomous driving.

## Interview explanation

I built this project to study robotics perception reliability under detection, association, latency, and dropped-frame constraints. The system runs YOLOv8n detections on KITTI tracking sequences `0000`–`0005`, tracks objects with ByteTrack, evaluates with native TrackEval KITTI HOTA/MOTA/IDF1, compares against a simple IoU tracker, stress-tests dropped-frame failures, profiles CPU/GPU detector latency, and adds deterministic risk diagnostics for unstable tracks. I also expose saved tracking outputs through ROS 2 Jazzy topics, publish robot-facing risk/safety status, added a compact C++ tracking core for latency-critical primitives, and built an online ROS 2 image-tracking smoke-test node that subscribes to `/camera/image_raw`.


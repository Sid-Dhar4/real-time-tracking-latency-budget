# Final Project Summary

## Project

Real-Time Object Tracking Under a Robotics Latency Budget

## One-line description

A reproducible robotics perception benchmark that evaluates YOLOv8n + ByteTrack object tracking on KITTI sequences with latency profiling, TrackEval metrics, failure analysis, robustness stress tests, and a simple IoU tracker baseline.

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

## Strongest measured results

- Six-sequence ByteTrack native TrackEval combined results: HOTA `46.634`, MOTA `50.354`, IDF1 `61.903` across `5,793` ground-truth detections
- Two-sequence controlled tracker comparison: ByteTrack IDF1 `68.385` vs simple IoU tracker IDF1 `58.949`
- ByteTrack vs simple IoU tracker: ID switches `42` vs `197`
- Dropped-frame stress test: HOTA degrades from `49.412` baseline to `25.852` when every 2nd frame is removed
- Warmup-aware CPU tracker p95 latency is approximately `16 ms` on both evaluated sequences
- ROS 2 diagnostics latency probe: receive p95 `0.608 ms`, internal publish p95 `0.156 ms` at 10 FPS replay
- ROS 2 debug image topic publishes annotated `sensor_msgs/Image` frames with track boxes and IDs

## Honest caveats

- This is not a public KITTI leaderboard submission.
- The detector is pretrained YOLOv8n, not trained from scratch.
- GPU benchmarking was not included because NVIDIA driver support was not working through `nvidia-smi`.
- The project focuses on tracking-by-detection benchmarking, not full autonomous driving.

## Interview explanation

I built this project to study robotics perception reliability under detection, association, latency, and dropped-frame constraints. The system runs YOLOv8n detections on KITTI tracking sequences `0000`–`0005`, tracks objects with ByteTrack, evaluates with native TrackEval KITTI HOTA/MOTA/IDF1, and adds local diagnostics for threshold sweeps and failure analysis. I also compare ByteTrack against a simple IoU tracker, stress-test dropped-frame failures, profile CPU latency, and expose saved tracking outputs through ROS 2 topics including `/tracking/objects`, `/tracking/status`, `/tracking/detections_2d`, `/tracking/diagnostics`, and `/tracking/debug_image`.

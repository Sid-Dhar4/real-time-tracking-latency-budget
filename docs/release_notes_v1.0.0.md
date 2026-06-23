# v1.0.0 Release Notes

## Real-Time Object Tracking Under a Robotics Latency Budget

This release freezes the project as a polished robotics perception benchmark and ROS 2 replay package.

## Core benchmark features

- YOLOv8n + ByteTrack tracking-by-detection pipeline on KITTI tracking data.
- Six-sequence native TrackEval KITTI benchmark on sequences `0000`–`0005`.
- Two-sequence TrackEval baseline on sequences `0000`–`0001`.
- Dropped-frame robustness stress tests.
- ByteTrack vs simple IoU tracker comparison.
- Warmup-aware CPU latency analysis.
- Failure analysis with worst-frame examples and ID-switch diagnostics.

## ROS 2 features

- ROS 2 Jazzy replay wrapper for saved KITTI tracking outputs.
- JSON compatibility topics: `/tracking/objects` and `/tracking/status`.
- Typed tracking topic: `/tracking/detections_2d` using `vision_msgs/Detection2DArray`.
- Typed diagnostics topic: `/tracking/diagnostics` using `diagnostic_msgs/DiagnosticArray`.
- Debug image topic: `/tracking/debug_image` using `sensor_msgs/Image`.
- Diagnostics latency probe with p95 receive latency of `0.608 ms` at 10 FPS replay.

## Reproducibility and trust

- GitHub Actions CI runs tests and artifact checks.
- `scripts/check_artifacts_exist.py` verifies key reports, plots, videos, media, ROS reports, and stale-claim wording.
- Curated dependency files are provided in `environment/`.
- The README includes a clickable demo GIF linked to the full annotated video.

## Honest caveats

- This is not a public KITTI leaderboard submission.
- The detector is pretrained YOLOv8n, not trained from scratch.
- GPU benchmarking is not claimed.
- The project focuses on tracking-by-detection reliability benchmarking, not a full autonomous driving stack.

## Release commit

This release is intended to be tagged as `v1.0.0` after tests and artifact checks pass.

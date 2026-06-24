# ROS 2 Tracking Replay Wrapper

This package provides a lightweight ROS 2 wrapper around the saved KITTI tracking outputs.

It replays saved KITTI tracking outputs from CSV and publishes JSON compatibility topics, typed tracking outputs, diagnostics, and annotated debug images on ROS 2 topics.

## Package

`ros2/ros2_tracking_latency`

## Topics

- `/tracking/objects` (`std_msgs/String`): per-frame tracked objects as JSON.
- `/tracking/status` (`std_msgs/String`): replay status, frame index, number of tracks, FPS, and publish latency.
- `/tracking/detections_2d` (`vision_msgs/Detection2DArray`): typed 2D tracked-object outputs.
- `/tracking/diagnostics` (`diagnostic_msgs/DiagnosticArray`): typed replay diagnostics.
- `/tracking/debug_image` (`sensor_msgs/Image`): annotated KITTI frames with tracking boxes and IDs.

## Build

Use system ROS 2 Python, not the Conda benchmark environment:

```bash
cd ~/projects/real-time-tracking-latency-budget/ros2
conda deactivate 2>/dev/null || true
source /opt/ros/jazzy/setup.bash
colcon build --packages-select ros2_tracking_latency
source install/setup.bash
```

## Dry run

```bash
ros2 run ros2_tracking_latency kitti_track_replay \
  --tracks-csv ../results/tracks/yolov8n_bytetrack_seq0001_tracks.csv \
  --sequence 0001 \
  --max-frames 5 \
  --dry-run
```

Expected dry-run output includes loaded row count, replayed frame count, and per-frame track counts.

## ROS replay

```bash
ros2 run ros2_tracking_latency kitti_track_replay \
  --tracks-csv ../results/tracks/yolov8n_bytetrack_seq0001_tracks.csv \
  --sequence 0001 \
  --fps 2 \
  --max-frames 8
```

Then inspect topics:

```bash
ros2 topic list | grep /tracking
ros2 topic echo /tracking/status --once
ros2 topic echo /tracking/objects --once
```

## Smoke-test result

The wrapper was built with `colcon`, discovered by `ros2 pkg executables`, run through `ros2 run`, and verified to publish `/tracking/objects`, `/tracking/status`, `/tracking/detections_2d`, `/tracking/diagnostics`, and `/tracking/debug_image`.

## Design note

The wrapper publishes JSON compatibility topics, typed `vision_msgs/Detection2DArray` tracking outputs, typed `diagnostic_msgs/DiagnosticArray` diagnostics, and a separate `/tracking/debug_image` stream as `sensor_msgs/Image`. The tracking, diagnostics, latency probe, and debug-image paths are kept as separate components so each part can be tested independently.

## ROS helper smoke check

The ROS 2 message helper conversion functions can be checked with system ROS Python:

```bash
conda deactivate 2>/dev/null || true
source /opt/ros/jazzy/setup.bash
python3 scripts/check_ros2_message_helpers.py
```

This validates `Detection2DArray`, `DiagnosticArray`, and debug-image helper behavior outside the Conda benchmark environment.



## Robot-facing risk topics

The track replay node also publishes deterministic reliability summaries:

- `/tracking/risk`: per-frame risk summary with max/mean risk, medium/high-risk counts, and safety state
- `/tracking/safety_status`: compact downstream-facing safety status with `nominal`, `caution`, or `degraded`

These topics are derived from `results/tables/m33_frame_risk_scores.csv` and are intended for monitoring and downstream planning experiments, not certified safety control.

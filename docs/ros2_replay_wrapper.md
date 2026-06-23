# ROS 2 Tracking Replay Wrapper

This package provides a lightweight ROS 2 wrapper around the saved KITTI tracking outputs.

It replays tracked objects from CSV and publishes JSON messages on ROS 2 topics.

## Package

`ros2/ros2_tracking_latency`

## Topics

- `/tracking/objects` (`std_msgs/String`): per-frame tracked objects as JSON.
- `/tracking/status` (`std_msgs/String`): replay status, frame index, number of tracks, FPS, and publish latency.

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

The wrapper was built with `colcon`, discovered by `ros2 pkg executables`, run through `ros2 run`, and verified to publish `/tracking/objects` and `/tracking/status`.

## Design note

The first wrapper intentionally avoids `cv_bridge` and image publishing because the benchmark Conda environment uses a different Python/NumPy stack than ROS 2 Jazzy system Python. The MVP publishes tracking objects and status first, which is robust and enough to demonstrate robotics integration.

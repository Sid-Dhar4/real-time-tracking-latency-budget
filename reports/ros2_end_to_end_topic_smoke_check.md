# ROS 2 End-to-End Topic Smoke Check

This report documents the end-to-end ROS 2 topic smoke check for the tracking latency replay wrapper.

## Purpose

The ROS 2 workspace smoke check proves that the package builds. This end-to-end check proves that the replay nodes actually run and publish expected robotics topics.

## Command

Run:

    bash scripts/check_ros2_end_to_end_topics.sh

## What the check verifies

The script builds the ROS 2 package in a temporary colcon workspace, launches the replay nodes, and listens for one message on each expected topic.

Verified topics:

- `/tracking/status` as `std_msgs/msg/String`
- `/tracking/objects` as `std_msgs/msg/String`
- `/tracking/detections_2d` as `vision_msgs/msg/Detection2DArray`
- `/tracking/diagnostics` as `diagnostic_msgs/msg/DiagnosticArray`
- `/tracking/debug_image` as `sensor_msgs/msg/Image`

## Input artifacts

- `results/tracks/yolov8n_bytetrack_seq0001_tracks.csv`
- `data/kitti_tracking/training/image_02/0001`

## Latest local result

The local end-to-end smoke check passed.

Observed samples included:

- `/tracking/status` with sequence, frame, track count, FPS, publish latency, and source CSV
- `/tracking/objects` with JSON track objects
- `/tracking/detections_2d` header with `frame_id: kitti_camera`
- `/tracking/diagnostics` header with `frame_id: tracking_latency`
- `/tracking/debug_image` header with `frame_id: kitti_camera`

The debug image replay node also logged successful publication of early frames with measured publish time.

## Claim boundary

This is a smoke test, not a long-duration runtime certification. It verifies that the ROS 2 replay package can build, launch, publish, and be observed through ROS 2 topics on a local ROS 2 Jazzy installation.

# ROS 2 Typed Tracking Topics

The ROS 2 replay wrapper publishes both compatibility JSON topics and robotics-native typed topics.

## Compatibility topics

- `/tracking/objects` — `std_msgs/msg/String`
- `/tracking/status` — `std_msgs/msg/String`

## Typed topics

- `/tracking/detections_2d` — `vision_msgs/msg/Detection2DArray`
- `/tracking/diagnostics` — `diagnostic_msgs/msg/DiagnosticArray`

## What is published

`/tracking/detections_2d` contains one `Detection2D` message per tracked object, including:

- `header.frame_id`
- persistent track ID in `id`
- class name in `results[].hypothesis.class_id`
- confidence in `results[].hypothesis.score`
- 2D bounding-box center and size

`/tracking/diagnostics` contains replay status fields:

- sequence
- frame
- number of tracks
- replay FPS
- publish latency in milliseconds
- source CSV path

## Smoke-test evidence

The typed wrapper was rebuilt with `colcon`, run through `ros2 run`, and verified with:

```bash
ros2 topic info /tracking/detections_2d
ros2 topic info /tracking/diagnostics
ros2 topic echo /tracking/detections_2d --once
ros2 topic echo /tracking/diagnostics --once
```

The smoke test confirmed:

- `/tracking/detections_2d` type: `vision_msgs/msg/Detection2DArray`
- `/tracking/diagnostics` type: `diagnostic_msgs/msg/DiagnosticArray`
- detections include track IDs, class labels, confidence scores, and bounding boxes
- diagnostics include frame, track count, FPS, publish latency, and source CSV

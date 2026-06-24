# Online ROS 2 Image Tracking Node

This report documents the online ROS 2 image tracking mode added to the project.

## Purpose

The main benchmark remains an offline and reproducible tracking benchmark over KITTI-style data. This online node adds a callback-driven ROS 2 perception mode to show how the same tracking, diagnostics, and risk/safety interface can be exposed from a live image stream.

The goal is not to replace the YOLOv8n + ByteTrack benchmark. The goal is to demonstrate a real ROS 2 perception-node architecture:

    /camera/image_raw -> image callback -> detection/tracking -> tracking topics + risk/safety topics

## Node

Executable:

    ros2 run ros2_tracking_latency image_iou_tracking

Source:

- ros2/ros2_tracking_latency/ros2_tracking_latency/image_iou_tracking_node.py

## Input

The node subscribes to:

- /camera/image_raw as sensor_msgs/msg/Image

Supported encodings for the smoke-test node:

- mono8
- 8UC1
- rgb8
- bgr8

## Online detector/tracker behavior

The node uses a deterministic bright-region detector for smoke-testability. It extracts connected bright regions, converts them to bounding boxes, and tracks them online using IoU association.

This is intentionally lightweight and reproducible. It is not claiming to outperform YOLO/ByteTrack.

## Published topics

The node publishes:

- /tracking/status as std_msgs/msg/String
- /tracking/objects as std_msgs/msg/String
- /tracking/detections_2d as vision_msgs/msg/Detection2DArray
- /tracking/diagnostics as diagnostic_msgs/msg/DiagnosticArray
- /tracking/risk as std_msgs/msg/String
- /tracking/safety_status as std_msgs/msg/String

## Risk and safety interface

The online node emits the same style of downstream-facing reliability signals used by the replay wrapper:

- max risk score
- mean risk score
- number of medium/high-risk tracks
- safety state: nominal, caution, or degraded
- reason string

## Smoke test

Run:

    bash scripts/check_ros2_online_image_tracking.sh

The smoke test:

1. Builds the ROS 2 package in a temporary colcon workspace.
2. Starts image_iou_tracking.
3. Publishes synthetic mono8 images to /camera/image_raw.
4. Verifies the tracking, detection, risk, and safety topics publish.

## Latest local result

The online smoke test passed. It observed two synthetic bright-object tracks and verified:

- /tracking/status
- /tracking/objects
- /tracking/detections_2d
- /tracking/risk
- /tracking/safety_status

Example observed status used mode online_image_iou with num_tracks equal to 2.

## Claim boundary

This is an online ROS 2 perception-node architecture demonstration, not a production detector. The project’s measured benchmark results still come from the KITTI-style YOLOv8n + ByteTrack pipeline. This node proves online ROS 2 integration and robot-facing diagnostic topic design.

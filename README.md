# Real-Time Object Tracking Under a Robotics Latency Budget

## Summary

This project builds a reproducible tracking-by-detection benchmark using a lightweight detector, ByteTrack, KITTI tracking data, tracking metrics, latency measurements, threshold sweeps, plots, and failure analysis.

## Why this project

Robot perception systems must trade off accuracy and latency. A tracker that is accurate but too slow may be unusable, while a fast tracker with many ID switches can be unreliable for deployment.

## Dataset

KITTI tracking training split with a local validation subset only. No public leaderboard submission.

## Systems compared

MVP:

- YOLOv8n detector
- ByteTrack tracker

Extensions after MVP:

- OC-SORT
- second detector
- CPU/GPU or ONNX comparison
- ROS 2 visualization
- optional C++ association module

## Pipeline

KITTI frames -> detector -> detections -> tracker -> tracks -> evaluation -> metrics.csv -> plots -> failure analysis.

## Results

Not measured yet.

## Accuracy-latency tradeoff

Not measured yet.

## Failure analysis

Not started yet.

## Reproduce

Commands will be added after each milestone.

## Tests

Tests will cover dataset parsing, detection/tracking formats, latency parsing, and result schemas.

## Limitations

Initial MVP uses pretrained detection and a small local KITTI validation split.

## Future work

OC-SORT comparison, second detector, ONNX inference, ROS 2 visualization, C++ association module, nuScenes-mini, and real camera video.

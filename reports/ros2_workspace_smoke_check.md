# ROS 2 Workspace Smoke Check

This report documents the local ROS 2 workspace smoke check for the tracking latency replay wrapper.

## Purpose

The repository includes a ROS 2 Jazzy package, `ros2_tracking_latency`, that replays saved KITTI tracking outputs as robotics-native topics.

The smoke check verifies that the package can be built and discovered in a clean temporary colcon workspace.

## Command

Run:

    bash scripts/check_ros2_workspace.sh

## What the check verifies

- ROS 2 Jazzy environment is available at `/opt/ros/jazzy/setup.bash`
- `ros2` CLI is discoverable
- `colcon` is available
- ROS 2 message helper checks pass
- ROS 2 Python ABI mismatch is avoided by using system Python for `rclpy`
- package builds in a temporary colcon workspace
- package `ros2_tracking_latency` is discoverable after build
- executables are discoverable:
  - `kitti_track_replay`
  - `kitti_debug_image_replay`

## Why system Python is used

The main benchmark environment uses conda Python 3.11. ROS 2 Jazzy on Ubuntu 24.04 provides `rclpy` for system Python 3.12.

Using conda Python to import `rclpy` can fail because the compiled `rclpy` extension is built for a different Python ABI. The smoke check intentionally uses `/usr/bin/python3` for ROS helper checks.

## Build hygiene

The script builds in a temporary directory created with `mktemp -d`. The temporary build, install, and log directories are removed automatically when the script exits.

This avoids committing local ROS build artifacts such as `build/`, `install/`, or `log/`.

## Latest local result

The smoke check passed locally:

- ROS distro: Jazzy
- Shell Python: conda Python 3.11.15
- System ROS Python: Python 3.12.3
- message helper checks: passed
- temporary colcon build: passed
- package discovery: passed
- executable discovery: passed

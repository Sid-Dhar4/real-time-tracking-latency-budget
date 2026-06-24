#!/usr/bin/env bash
set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "========== ROS 2 ENVIRONMENT =========="

if [ -f /opt/ros/jazzy/setup.bash ]; then
  # ROS setup files may reference optional unset variables, so do not use set -u here.
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
else
  echo "ERROR: /opt/ros/jazzy/setup.bash not found."
  echo "Install ROS 2 Jazzy or run this check on a machine with ROS 2 Jazzy."
  exit 2
fi

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
which ros2
ros2 pkg list >/dev/null

echo
echo "========== PYTHON ABI CHECK =========="
echo "Shell python:"
which python || true
python --version || true

echo "System ROS python:"
/usr/bin/python3 --version

echo
echo "========== COLCON CHECK =========="
if ! command -v colcon >/dev/null 2>&1; then
  echo "ERROR: colcon not found. Install python3-colcon-common-extensions."
  exit 2
fi
which colcon

echo
echo "========== ROS 2 MESSAGE HELPER SMOKE CHECK =========="
# ROS 2 Jazzy rclpy is built for system Python 3.12 on Ubuntu 24.04.
# Do not use the conda Python 3.11 interpreter for this check.
/usr/bin/python3 scripts/check_ros2_message_helpers.py

echo
echo "========== TEMPORARY COLCON BUILD =========="

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

colcon --log-base "$TMP_ROOT/log" build \
  --base-paths ros2/ros2_tracking_latency \
  --build-base "$TMP_ROOT/build" \
  --install-base "$TMP_ROOT/install" \
  --event-handlers console_cohesion+

# shellcheck disable=SC1091
source "$TMP_ROOT/install/setup.bash"

echo
echo "========== ROS 2 PACKAGE DISCOVERY =========="
ros2 pkg prefix ros2_tracking_latency
ros2 pkg executables ros2_tracking_latency

ros2 pkg executables ros2_tracking_latency | grep -q "kitti_track_replay"
ros2 pkg executables ros2_tracking_latency | grep -q "kitti_debug_image_replay"

echo
echo "ROS 2 workspace smoke check passed."

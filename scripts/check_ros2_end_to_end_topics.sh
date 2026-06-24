#!/usr/bin/env bash
set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "========== ROS 2 ENVIRONMENT =========="

if [ -f /opt/ros/jazzy/setup.bash ]; then
  # ROS setup files may reference optional unset variables, so do not use set -u.
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
else
  echo "ERROR: /opt/ros/jazzy/setup.bash not found."
  exit 2
fi

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
which ros2
/usr/bin/python3 --version

echo
echo "========== INPUT ARTIFACTS =========="
TRACKS_CSV="results/tracks/yolov8n_bytetrack_seq0001_tracks.csv"
IMAGE_DIR="data/kitti_tracking/training/image_02/0001"

test -f "$TRACKS_CSV"
test -d "$IMAGE_DIR"

ls -lh "$TRACKS_CSV"
/usr/bin/python3 - <<'PYIMG'
from pathlib import Path
image_dir = Path("data/kitti_tracking/training/image_02/0001")
for path in sorted(image_dir.glob("*.png"))[:3]:
    print(path)
PYIMG

echo
echo "========== TEMPORARY COLCON BUILD =========="

TMP_ROOT="$(mktemp -d)"
trap 'set +e; kill ${TRACK_NODE_PID:-0} ${DEBUG_NODE_PID:-0} 2>/dev/null; rm -rf "$TMP_ROOT"' EXIT

colcon --log-base "$TMP_ROOT/log" build \
  --base-paths ros2/ros2_tracking_latency \
  --build-base "$TMP_ROOT/build" \
  --install-base "$TMP_ROOT/install" \
  --event-handlers console_cohesion+

# shellcheck disable=SC1091
source "$TMP_ROOT/install/setup.bash"

echo
echo "========== PACKAGE DISCOVERY =========="
ros2 pkg prefix ros2_tracking_latency
ros2 pkg executables ros2_tracking_latency

echo
echo "========== TRACK REPLAY TOPIC CHECK =========="

timeout 15s ros2 topic echo --once /tracking/status std_msgs/msg/String > "$TMP_ROOT/status.txt" &
STATUS_PID=$!

timeout 15s ros2 topic echo --once /tracking/objects std_msgs/msg/String > "$TMP_ROOT/objects.txt" &
OBJECTS_PID=$!

timeout 15s ros2 topic echo --once /tracking/detections_2d vision_msgs/msg/Detection2DArray --field header > "$TMP_ROOT/detections_header.txt" &
DETECTIONS_PID=$!

timeout 15s ros2 topic echo --once /tracking/diagnostics diagnostic_msgs/msg/DiagnosticArray --field header > "$TMP_ROOT/diagnostics_header.txt" &
DIAGNOSTICS_PID=$!

ros2 run ros2_tracking_latency kitti_track_replay \
  --tracks-csv "$TRACKS_CSV" \
  --sequence 0001 \
  --fps 5 \
  --max-frames 20 \
  --frame-id kitti_camera \
  > "$TMP_ROOT/track_node.log" 2>&1 &
TRACK_NODE_PID=$!

wait "$STATUS_PID"
wait "$OBJECTS_PID"
wait "$DETECTIONS_PID"
wait "$DIAGNOSTICS_PID"

wait "$TRACK_NODE_PID" || true

echo "status sample:"
head -20 "$TMP_ROOT/status.txt"

echo
echo "objects sample:"
head -20 "$TMP_ROOT/objects.txt"

echo
echo "detections header sample:"
cat "$TMP_ROOT/detections_header.txt"

echo
echo "diagnostics header sample:"
cat "$TMP_ROOT/diagnostics_header.txt"

grep -q "sequence" "$TMP_ROOT/status.txt"
grep -q "objects" "$TMP_ROOT/objects.txt"
grep -q "frame_id" "$TMP_ROOT/detections_header.txt"
grep -q "frame_id" "$TMP_ROOT/diagnostics_header.txt"

echo
echo "========== DEBUG IMAGE TOPIC CHECK =========="

timeout 15s ros2 topic echo --once /tracking/debug_image sensor_msgs/msg/Image --field header > "$TMP_ROOT/debug_image_header.txt" &
DEBUG_IMAGE_PID=$!

ros2 run ros2_tracking_latency kitti_debug_image_replay \
  --tracks-csv "$TRACKS_CSV" \
  --image-dir "$IMAGE_DIR" \
  --sequence 0001 \
  --fps 5 \
  --max-frames 20 \
  --frame-id kitti_camera \
  > "$TMP_ROOT/debug_node.log" 2>&1 &
DEBUG_NODE_PID=$!

wait "$DEBUG_IMAGE_PID"
wait "$DEBUG_NODE_PID" || true

echo "debug image header sample:"
cat "$TMP_ROOT/debug_image_header.txt"

grep -q "frame_id" "$TMP_ROOT/debug_image_header.txt"

echo
echo "========== NODE LOG SAMPLES =========="
echo "--- track node ---"
tail -20 "$TMP_ROOT/track_node.log"

echo
echo "--- debug node ---"
tail -20 "$TMP_ROOT/debug_node.log"

echo
echo "ROS 2 end-to-end topic smoke check passed."

#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

set +u
source /opt/ros/jazzy/setup.bash
set -u

TMP_ROOT="$(mktemp -d)"
WS_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT" "$WS_ROOT"' EXIT

echo "========== ROS 2 ENVIRONMENT =========="
echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
which ros2
/usr/bin/python3 --version

echo
echo "========== TEMPORARY COLCON BUILD =========="
mkdir -p "$WS_ROOT/src"
cp -a ros2/ros2_tracking_latency "$WS_ROOT/src/"

cd "$WS_ROOT"
colcon build --packages-select ros2_tracking_latency --event-handlers console_direct+
set +u
source "$WS_ROOT/install/setup.bash"
set -u

cd "$REPO_ROOT"

echo
echo "========== PACKAGE DISCOVERY =========="
ros2 pkg prefix ros2_tracking_latency
ros2 pkg executables ros2_tracking_latency

echo
echo "========== ONLINE IMAGE TRACKING TOPIC CHECK =========="

timeout 15s ros2 topic echo --once /tracking/status std_msgs/msg/String > "$TMP_ROOT/status.txt" &
STATUS_PID=$!

timeout 15s ros2 topic echo --once /tracking/objects std_msgs/msg/String > "$TMP_ROOT/objects.txt" &
OBJECTS_PID=$!

timeout 15s ros2 topic echo --once /tracking/detections_2d vision_msgs/msg/Detection2DArray --field header > "$TMP_ROOT/detections_header.txt" &
DETECTIONS_PID=$!

timeout 15s ros2 topic echo --once /tracking/risk std_msgs/msg/String > "$TMP_ROOT/risk.txt" &
RISK_PID=$!

timeout 15s ros2 topic echo --once /tracking/safety_status std_msgs/msg/String > "$TMP_ROOT/safety_status.txt" &
SAFETY_PID=$!

timeout 20s ros2 run ros2_tracking_latency image_iou_tracking \
  --image-topic /camera/image_raw \
  --threshold 200 \
  --min-area 20 \
  --iou-threshold 0.3 \
  --max-age 2 \
  --class-name bright_object \
  --frame-id camera \
  > "$TMP_ROOT/online_node.log" 2>&1 &
NODE_PID=$!

sleep 1

/usr/bin/python3 - <<'PY'
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

class SyntheticImagePublisher(Node):
    def __init__(self):
        super().__init__("synthetic_image_publisher")
        self.pub = self.create_publisher(Image, "/camera/image_raw", 10)

    def publish_frame(self, frame_index):
        width = 64
        height = 64
        data = bytearray(width * height)

        # Moving bright square.
        x0 = 10 + frame_index
        y0 = 20
        for y in range(y0, y0 + 10):
            for x in range(x0, x0 + 10):
                data[y * width + x] = 255

        # Second static bright square.
        for y in range(40, 48):
            for x in range(42, 50):
                data[y * width + x] = 230

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera"
        msg.height = height
        msg.width = width
        msg.encoding = "mono8"
        msg.is_bigendian = 0
        msg.step = width
        msg.data = bytes(data)

        self.pub.publish(msg)

rclpy.init()
node = SyntheticImagePublisher()

for i in range(8):
    node.publish_frame(i)
    rclpy.spin_once(node, timeout_sec=0.05)
    time.sleep(0.15)

node.destroy_node()
rclpy.shutdown()
PY

wait "$STATUS_PID"
wait "$OBJECTS_PID"
wait "$DETECTIONS_PID"
wait "$RISK_PID"
wait "$SAFETY_PID"

wait "$NODE_PID" || true

echo
echo "status sample:"
cat "$TMP_ROOT/status.txt"

echo
echo "objects sample:"
cat "$TMP_ROOT/objects.txt"

echo
echo "detections header sample:"
cat "$TMP_ROOT/detections_header.txt"

echo
echo "risk sample:"
cat "$TMP_ROOT/risk.txt"

echo
echo "safety status sample:"
cat "$TMP_ROOT/safety_status.txt"

echo
echo "node log sample:"
cat "$TMP_ROOT/online_node.log"

grep -q "online_image_iou" "$TMP_ROOT/status.txt"
grep -q "objects" "$TMP_ROOT/objects.txt"
grep -q "frame_id" "$TMP_ROOT/detections_header.txt"
grep -q "max_risk_score" "$TMP_ROOT/risk.txt"
grep -q "safety_state" "$TMP_ROOT/safety_status.txt"

echo
echo "ROS 2 online image tracking smoke check passed."

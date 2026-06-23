# ROS 2 Debug Image Replay

The ROS 2 package includes a debug image replay node that publishes annotated KITTI frames with tracking boxes and IDs.

## Executable

```bash
ros2 run ros2_tracking_latency kitti_debug_image_replay
```

## Topic

- `/tracking/debug_image` — `sensor_msgs/msg/Image`

## What it publishes

The node reads KITTI image frames and saved ByteTrack CSV output, draws tracked boxes and IDs, and publishes annotated images as `bgr8` ROS images.

## Smoke-test evidence

The debug image node was built with `colcon`, discovered by `ros2 pkg executables`, and verified with a Python subscriber.

Observed sample:

- topic: `/tracking/debug_image`
- type: `sensor_msgs/msg/Image`
- frame_id: `kitti_camera`
- height: `375`
- width: `1242`
- encoding: `bgr8`
- data length: `1397250`

Static sample artifact:

- `media/tracking_debug_image_sample.jpg`

# ROS 2 package

This directory contains a ROS 2 Jazzy replay wrapper for the tracking latency benchmark.

Build with system ROS 2 Python, not Conda:

```bash
cd ros2
conda deactivate 2>/dev/null || true
source /opt/ros/jazzy/setup.bash
colcon build --packages-select ros2_tracking_latency
source install/setup.bash
ros2 run ros2_tracking_latency kitti_track_replay --dry-run
```

See `docs/ros2_replay_wrapper.md` from the repository root for details.

# ROS 2 Latency Probe

This report measures the ROS 2 diagnostics message path for the tracking replay wrapper.

## Method

- Start the `kitti_track_replay` ROS 2 node at 10 FPS.
- Publish typed diagnostics on `/tracking/diagnostics`.
- Subscribe with `scripts/ros2_diagnostic_latency_probe.py`.
- Compare the received ROS time against the `DiagnosticArray.header.stamp`.
- Save per-message measurements to `results/tables/m26_ros2_latency_probe.csv`.

## Summary

- Samples: `30`
- Sequence: `0001`
- Replay FPS: `10.0`
- ROS receive latency mean: `0.512` ms
- ROS receive latency p50: `0.494` ms
- ROS receive latency p95: `0.608` ms
- ROS receive latency max: `0.898` ms
- Internal message construction/publish latency mean: `0.125` ms
- Internal message construction/publish latency p95: `0.156` ms

## Notes

This is a local ROS 2 replay-path measurement, not a full detector-to-planner end-to-end latency trace. It verifies that the typed diagnostics topic can be monitored and summarized as part of a robotics perception pipeline.

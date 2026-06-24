# Release Notes — v1.2.0

## Summary

v1.2.0 packages the repository as a stronger robotics perception portfolio project. It extends the v1.1.0 benchmark/replay release with reliability diagnostics, robot-facing risk/safety topics, a C++ tracking core, and an online ROS 2 image-tracking smoke-test node.

## Added

- Risk-vs-failure correlation report showing that risk aligns with track fragmentation and frame-level FP/FN burden while ID switches remain a separate long-track identity-consistency failure mode.
- Robot-facing ROS 2 risk/safety topics:
  - `/tracking/risk`
  - `/tracking/safety_status`
- C++ tracking core with:
  - IoU computation
  - greedy association
  - track lifecycle state
  - risk scoring
  - unit tests
  - microbenchmark
- Online ROS 2 image tracking node:
  - subscribes to `/camera/image_raw`
  - performs deterministic bright-region detection plus IoU tracking
  - publishes tracking, typed detection, diagnostics, risk, and safety-status topics
- Online ROS 2 smoke test with synthetic image publisher.
- Final stale-documentation cleanup for recruiter-facing consistency.

## Validation

Local validation includes:

    bash scripts/run_tests.sh
    python scripts/check_artifacts_exist.py
    bash scripts/check_cpp_tracking_core.sh
    bash scripts/check_ros2_workspace.sh
    bash scripts/check_ros2_end_to_end_topics.sh
    bash scripts/check_ros2_online_image_tracking.sh

GitHub Actions validates Python tests, the C++ tracking core, and artifact/stale-claim checks.

## Claim boundaries

- This is not a public KITTI leaderboard submission.
- The online ROS 2 image node is a smoke-testable architecture demo, not the measured YOLOv8n + ByteTrack benchmark pipeline.
- The risk score is a deterministic diagnostic heuristic, not a certified safety metric.

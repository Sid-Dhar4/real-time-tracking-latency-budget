# Limitations

- Results are local reproducible evaluations on KITTI training sequences, not a public KITTI test-server or leaderboard submission.
- The detector uses pretrained YOLOv8n weights, not a KITTI-trained or project-specific fine-tuned detector.
- The measured benchmark results come from the KITTI-style YOLOv8n + ByteTrack pipeline; the online ROS 2 node uses a deterministic bright-region detector for smoke-testable architecture validation.
- The CPU/GPU latency benchmark measures detector inference on preloaded KITTI frames; it does not include camera transport, full ROS 2 perception graph latency, planner latency, or actuation.
- The track reliability risk score is a deterministic diagnostic heuristic, not a learned uncertainty model or safety certification metric.
- The tracker comparison covers ByteTrack versus a simple IoU tracker baseline; it is not an exhaustive comparison against all modern tracking systems.
- The visual demo is qualitative; the primary evidence is in the checked-in reports, metrics tables, plots, tests, CI, and reproduction matrix.

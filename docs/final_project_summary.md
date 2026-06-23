# Final Project Summary

## Project

Real-Time Object Tracking Under a Robotics Latency Budget

## One-line description

A reproducible robotics perception benchmark that evaluates YOLOv8n + ByteTrack object tracking on KITTI sequences with latency profiling, TrackEval metrics, failure analysis, robustness stress tests, and a simple IoU tracker baseline.

## What was built

- KITTI tracking benchmark pipeline for sequences `0000` and `0001`
- YOLOv8n detector outputs
- ByteTrack tracker outputs
- Local KITTI-style evaluator
- Native TrackEval KITTI evaluation
- Confidence-threshold sweep
- Warmup-aware CPU latency summaries and plots
- Annotated demo video
- Dropped-frame robustness stress test
- Simple IoU tracker baseline for algorithm comparison
- Tests for schema and dataset sanity

## Strongest measured results

- ByteTrack native TrackEval combined results: HOTA `49.412`, MOTA `52.312`, IDF1 `68.385`
- ByteTrack vs simple IoU tracker: IDF1 `68.385` vs `58.949`
- ByteTrack vs simple IoU tracker: ID switches `42` vs `197`
- Dropped-frame stress test: HOTA degrades from `49.412` baseline to `25.852` when every 2nd frame is removed
- Warmup-aware CPU tracker p95 latency is approximately `16 ms` on both evaluated sequences

## Honest caveats

- This is not a public KITTI leaderboard submission.
- The detector is pretrained YOLOv8n, not trained from scratch.
- GPU benchmarking was not included because NVIDIA driver support was not working through `nvidia-smi`.
- The project focuses on tracking-by-detection benchmarking, not full autonomous driving.

## Interview explanation

I built this project to study the robotics perception tradeoff between detection quality, tracker identity consistency, and runtime latency. The system runs YOLOv8n detections on KITTI tracking sequences, tracks objects with ByteTrack, evaluates using both local KITTI-style metrics and native TrackEval KITTI metrics, and then analyzes how performance changes under confidence thresholds, dropped-frame failures, and a simple IoU tracker baseline. The key result is that ByteTrack gives stronger identity consistency than a geometric IoU baseline, while dropped-frame stress tests show how intermittent perception output causes HOTA, MOTA, and IDF1 to degrade.

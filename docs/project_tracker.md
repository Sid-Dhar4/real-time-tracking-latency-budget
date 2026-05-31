# Project Tracker — Real-Time Object Tracking Under a Robotics Latency Budget

## Current active milestone

| Active Milestone | Status | Next action |
| ---------------- | ------ | ----------- |
| M7 | not started | polish README, resume bullets, screenshots, and interview notes |

## Milestone tracker

| Milestone | Goal | Status | Evidence artifact | Commit |
| --------- | ---- | ------ | ----------------- | ------ |
| M0 | Repo skeleton + environment audit | complete | results/logs/environment_audit.txt | 76316d2 |
| M1 | Dataset prep + split config | complete | results/tables/dataset_summary.csv | 52324da |
| M2 | Detector inference on one sequence | complete | results/logs/m2_detector_smoke_test.txt | 93319cf |
| M3 | Tracker integration on one sequence | complete | results/logs/m3_tracker_smoke_test.txt + results/tables/m3_tracker_summary.csv | pending |
| M4 | Local KITTI-style evaluation working | complete | results/metrics.csv + results/logs/m4_local_eval.txt | pending |
| M5 | Confidence threshold sweep + latency benchmark | complete | results/sweep_results.csv + results/plots/m5_confidence_sweep_latency_idf1.png | pending |
| M6 | Failure analysis | complete | reports/failure_analysis.md + results/failure_cases/m6_*.jpg | pending |
| M7 | README/demo/resume/interview polish | not started | final artifacts | |

## Block tracker

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M0A-M0K | Repo skeleton, environment audit, tracker cleanup | complete |
| M1A-M1P | KITTI download, extraction, split verification | complete |
| M2A-M2K | Conda env, YOLOv8n detector, full sequence detector run | complete |
| M3A | Mark M3 active and allow M3 tracker log evidence | complete |
| M3B | Write ByteTrack tracker config | not started |
| M3C | Write tracker integration script | not started |
| M3D | Run ByteTrack tracker smoke test | not started |
| M3E | Commit tracker smoke test evidence | complete |
| M3F | Freeze environment after ByteTrack dependency install | complete |
| M3G | Run ByteTrack tracker on full KITTI sequence 0000 | complete |
| M3H | Create simple tracker summary table | complete |
| M3I | Update project tracker and allow M3 summary evidence | complete |
| M3J | Commit full-sequence tracker evidence | complete |
| M4A | Mark M4 active and allow evaluation evidence | complete |
| M4B | Write local KITTI-style evaluator | complete |
| M4C | Run local evaluation on Car class | complete |
| M4D | Commit local evaluation evidence | complete |

## MVP lock

First MVP only:

- KITTI tracking local split
- YOLOv8n pretrained detector
- ByteTrack tracker
- one or two KITTI sequences
- detections CSV
- tracks CSV
- latency CSV
- metrics CSV
- one threshold sweep
- one demo video/GIF
- failure analysis
- README and resume/interview polish

Not yet:

- ROS 2
- C++
- ONNX
- OC-SORT
- detector training
- multiple datasets
- public leaderboard submission

## Known risk

NVIDIA GPU is visible on PCI but nvidia-smi is not working. Current detector/tracker smoke tests use CPU. GPU benchmarking comes later.

## Rules

- Every runnable command block must have a START and END label.
- Every milestone must produce an evidence artifact.
- Every result must come from a script, saved CSV, log, plot, or generated report.
- Do not add fake metrics.
- Do not over-scope before the MVP works.


## M5 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M5A | Mark M5 active and allow sweep evidence | complete |
| M5B | Write confidence sweep script | complete |
| M5C | Run confidence threshold sweep | complete |
| M5D | Commit sweep evidence | complete |


## M6 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M6A | Mark M6 active and allow failure-analysis evidence | complete |
| M6B | Write failure analysis report script | complete |
| M6C | Run failure analysis | complete |
| M6D | Commit failure analysis evidence | complete |

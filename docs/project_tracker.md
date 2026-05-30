# Project Tracker — Real-Time Object Tracking Under a Robotics Latency Budget

## Current active milestone

| Active Milestone | Status | Next action |
| ---------------- | ------ | ----------- |
| M1 | not started | prepare KITTI dataset structure and split config |

## Milestone tracker

| Milestone | Goal | Status | Evidence artifact | Commit |
| --------- | ---- | ------ | ----------------- | ------ |
| M0 | Repo skeleton + environment audit | complete | results/logs/environment_audit.txt | 23fc321 |
| M1 | Dataset prep + split config | not started | results/tables/dataset_summary.csv | |
| M2 | Detector inference on one sequence | not started | detections CSV + sample image | |
| M3 | Tracker integration on one sequence | not started | tracked video/GIF | |
| M4 | TrackEval/evaluation working | not started | metrics CSV | |
| M5 | Threshold sweep + latency benchmark | not started | Pareto plot | |
| M6 | Failure analysis | not started | failure cases page | |
| M7 | README/demo/resume/interview polish | not started | final artifacts | |

## Block tracker

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M0A | Repair README, gitignore, tracker, and MVP scope | complete |
| M0B | Configure local Git identity | complete |
| M0C | Commit repo skeleton | complete |
| M0D | Verify M0 artifacts | complete |
| M0E | Refresh environment audit with Python3 and GPU diagnostics | complete |
| M0F | Close M0 in project tracker | complete |
| M0G | Commit M0 closeout | complete |
| M0H | Final M0 verification | complete |
| M0I | Track environment audit and finalize M0 tracker | complete |
| M0J | Commit final M0 cleanup | not started |

## M0 evidence

- Repo skeleton created.
- First commit created.
- Environment audit saved to results/logs/environment_audit.txt.
- Local Git identity configured for this repo.
- Tracker file created and maintained.

## M0 important findings

- Ubuntu 24.04.4 LTS detected.
- CPU: AMD Ryzen 7 8745HX with Radeon Graphics.
- Conda detected.
- System `python` command is not available yet.
- System `python3` is available.
- NVIDIA GPU is visible on PCI as an NVIDIA device.
- NVIDIA driver is not currently working through `nvidia-smi`.
- This GPU issue is a known risk for later GPU latency benchmarking, but it does not block M1 dataset prep.

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

## Rules

- Every runnable command block must have a START and END label.
- Every milestone must produce an evidence artifact.
- Every result must come from a script, saved CSV, log, plot, or generated report.
- Do not add fake metrics.
- Do not over-scope before the MVP works.

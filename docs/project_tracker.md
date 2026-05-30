# Project Tracker — Real-Time Object Tracking Under a Robotics Latency Budget

## Current active milestone

| Active Milestone | Status | Next action |
| ---------------- | ------ | ----------- |
| M1 | not started | prepare KITTI dataset structure and split config |

## Milestone tracker

| Milestone | Goal | Status | Evidence artifact | Commit |
| --------- | ---- | ------ | ----------------- | ------ |
| M0 | Repo skeleton + environment audit | complete | results/logs/environment_audit.txt | f346649 |
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
| M0G | Commit M0 closeout | not started |

## M0 evidence

- Repo skeleton created.
- First commit created.
- Environment audit saved to results/logs/environment_audit.txt.
- Local Git identity configured for this repo.

## M0 important findings

- Ubuntu 24.04.4 LTS detected.
- CPU: AMD Ryzen 7 8745HX with Radeon Graphics.
- Conda detected.
- The command `python` is not available yet, but `python3` should be checked and Conda will be used for the project environment.
- NVIDIA driver is not currently visible through `nvidia-smi`. This is a known risk for later GPU latency benchmarking.

## Rules

- Every runnable command block must have a START and END label.
- Every milestone must produce an evidence artifact.
- Every result must come from a script, saved CSV, log, plot, or generated report.
- Do not add fake metrics.
- Do not over-scope before the MVP works.

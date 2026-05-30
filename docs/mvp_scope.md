# MVP Scope

## Smallest impressive version

Build a reproducible tracking-by-detection benchmark on a small KITTI tracking subset.

The first MVP uses:

- KITTI tracking training split with a documented local validation subset
- YOLOv8n pretrained detector
- ByteTrack tracker
- saved detection outputs
- saved tracking outputs
- latency measurements
- FPS, mean latency, and p95 latency
- one confidence-threshold sweep
- one demo video or GIF
- failure analysis notes
- clean README and reproduction commands

## Core project question

How well does a lightweight detector plus tracker perform under a robotics-style latency budget?

## What this project is

A careful robotics computer vision benchmark.

## What this project is not

It is not a generic YOLO demo.
It is not a fake autonomous driving system.
It is not a leaderboard submission.
It is not a training project.
It is not a ROS 2 project yet.

## First MVP milestones

| Milestone | Goal | Output |
| --------- | ---- | ------ |
| M0 | Repo skeleton + environment audit | environment_audit.txt |
| M1 | Dataset prep + split config | dataset_summary.csv |
| M2 | Detector on one sequence | detections CSV + sample visualization |
| M3 | Tracker on one sequence | tracks CSV + demo video |
| M4 | Evaluation/export working | metrics.csv |
| M5 | Latency + threshold sweep | latency.csv + Pareto plot |
| M6 | Failure analysis | failure_analysis.md |
| M7 | Portfolio polish | README + resume bullets + interview notes |

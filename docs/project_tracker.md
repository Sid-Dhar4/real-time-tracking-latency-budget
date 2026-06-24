# Project Tracker — Real-Time Object Tracking Under a Robotics Latency Budget

## Current active milestone

| Active Milestone | Status | Next action |
| ---------------- | ------ | ----------- |
| M39 | complete | ROS 2 end-to-end topic smoke check |

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
| M7 | README/demo/resume/interview polish | complete | README.md + docs/resume_bullets.md + docs/interview_notes.md | pending |

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


## M7 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M7A | Mark M7 active | complete |
| M7B | Write portfolio polish docs | complete |
| M7C | Verify README, reports, resume bullets, and interview notes | complete |
| M7D | Commit M7 portfolio polish | complete |

## M8 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M8A | Verify MVP clean state and seq0001 dataset | complete |
| M8B | Create seq0001 configs and patch evaluator | complete |
| M8C | Run detector and tracker on seq0001 | complete |
| M8D | Evaluate seq0001 local KITTI-style Car tracking | complete |
| M8E | Create multi-sequence comparison table | complete |
| M8F | Allow M8 evidence files and update tracker | complete |
| M8G | Commit M8 evidence | complete |

## M9 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M9A | Create warmup-aware latency summary | complete |
| M9B | Allow M9 evidence and update tracker | complete |
| M9C | Commit M9 latency evidence | complete |

| M9D | Rebuild latency report without tabulate | complete |
| M9E | Commit fixed latency report and mark M9 complete | complete |

## M10 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M10A | Add schema and result sanity tests | complete |
| M10B | Initial pytest run exposed ROS plugin issue | complete |
| M10E | Run tests with ROS pytest plugin autoload disabled | complete |
| M10F | Add safe pytest runner | complete |
| M10H | Fix sequence ID normalization in tests | complete |
| M10I | Rerun schema tests successfully | complete |
| M10J | Commit and push passing schema tests | complete |

## M11 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M11A | Add annotated demo video script | complete |
| M11B | Generate annotated seq0001 demo video | complete |
| M11C | Add demo notes and allow demo artifacts | complete |
| M11D | Commit and push demo video artifacts | complete |

## M12 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M12A | Add latency plotting script | complete |
| M12B | Generate latency plots and runtime report | complete |
| M12C | Allow M12 plots and update tracker | complete |
| M12D | Commit and push latency plots | complete |

## M13 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M13A | Clone TrackEval and inspect runner | complete |
| M13B | Inspect TrackEval data layout | complete |
| M13C | Confirm native KITTI support and parser format | complete |
| M13D | Export KITTI TrackEval native-format files | complete |
| M13E | Run TrackEval KITTI car evaluation | complete |
| M13F | Capture and commit TrackEval artifacts | complete |

## M14 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M14A | Add dropped-frame stress exporter | complete |
| M14B | Generate stress-test tracker variants | complete |
| M14C | Run TrackEval on stress variants | complete |
| M14D | Summarize stress-test results | complete |
| M14E | Document and commit stress-test evidence | complete |

## M15 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M15A | Add simple IoU tracker baseline | complete |
| M15B | Run IoU tracker on KITTI sequences | complete |
| M15C | Export IoU tracker to TrackEval format | complete |
| M15D | Run TrackEval tracker comparison | complete |
| M15E | Summarize tracker comparison | complete |
| M15F | Commit tracker comparison evidence | complete |

## M16 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M16A | Add README key-results section and final project summary | complete |
| M16B | Commit final README/project summary polish | complete |

## M18 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M18A | Split bloated requirements into minimal/dev/full-lock files | complete |
| M18B | Verify imports, scripts, and tests after dependency cleanup | complete |
| M18C | Document curated environment and update tracker | complete |

## M19 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M19A | Add artifact and stale-claim checker | complete |
| M19B | Add GitHub Actions test workflow | complete |
| M19C | Document CI and update tracker | complete |

## M20 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M20A | Add simple IoU tracker unit tests | complete |
| M20B | Add benchmark artifact and metric sanity tests | complete |
| M20C | Document stronger tests and update tracker | complete |

## M21 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M21A | Create configs for KITTI sequences 0002-0005 | complete |
| M21B | Run full detector and ByteTrack outputs for 0002-0005 | complete |
| M21C | Export all six sequences to native TrackEval format | complete |
| M21D | Run six-sequence native TrackEval evaluation | complete |
| M21E | Summarize six-sequence benchmark artifacts | complete |
| M21F | Document and commit six-sequence benchmark | in progress |

## M22 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M22A | Verify ROS 2 Jazzy system Python environment | complete |
| M22B | Add ROS 2 package skeleton | complete |
| M22C | Add CSV-based KITTI track replay node | complete |
| M22D | Build with colcon and smoke-test ROS topics | complete |
| M22E | Document ROS 2 wrapper | complete |

## M23 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M23A | Create README GIF, poster, and MP4 media assets | complete |
| M23B | Add clickable hero GIF to README | complete |
| M23C | Add visual artifacts section | complete |
| M23D | Update artifact checker and tracker | complete |

## M24 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M24A | Audit reviewer consistency issues | complete |
| M24B | Fix README and final summary stale wording | complete |
| M24C | Run consistency checks and update tracker | complete |

## M25 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M25A | Check ROS typed-message dependencies | complete |
| M25B | Add vision_msgs Detection2DArray and diagnostic_msgs DiagnosticArray publishers | complete |
| M25C | Rebuild and smoke-test typed ROS topics | complete |
| M25D | Document typed ROS topics and update checks | complete |

## M26 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M26A | Create diagnostics latency probe script | complete |
| M26B | Run ROS 2 replay and collect diagnostics latency CSV | complete |
| M26C | Summarize latency probe results | complete |
| M26D | Update docs, artifact checks, and commit | complete |

## M27 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M27A | Audit KITTI images and ROS image dependencies | complete |
| M27B | Add debug image replay executable | complete |
| M27C | Build and smoke-test `/tracking/debug_image` | complete |
| M27D | Document debug image topic and update checks | complete |

## M29 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M29A | Final release audit | complete |
| M29B | Create release notes and update checks | complete |
| M29C | Commit release notes | complete |
| M29D | Tag `v1.0.0` | complete |

## M32 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M32A | Audit ROS helper functions | complete |
| M32B | Attempt pytest ROS helper tests | replaced by smoke check |
| M32C | Add system-Python ROS helper smoke script | complete |
| M32D | Commit smoke script | complete |
| M32E | Verify GitHub Actions | complete |
| M32F | Document smoke check and artifact requirement | complete |

## M33 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M33A | Audit track CSVs for risk scoring | complete |
| M33B | Add deterministic track risk scoring script | complete |
| M33C | Add risk tests and report | complete |
| M33D | Update docs, artifact checks, and commit | complete |

## M34 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M34A | Audit risk-score buckets | complete |
| M34B | Generate bucket summary, plot, report, and docs | complete |

## M35 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M35A | Audit NVIDIA driver, PyTorch CUDA, and Ultralytics | complete |
| M35B | Document initial runtime environment and GPU benchmark limitation | complete |
| M35C | Regenerate audit after CUDA PyTorch enablement | complete |

## M36 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M36A | Inspect existing benchmark path and CUDA state | complete |
| M36B | Add and run measured CPU/GPU latency benchmark | complete |
| M36C | Add report, docs, artifact checks, and commit | in progress |

## M37 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M37A | Audit README and reproduction docs | complete |
| M37B | Add reproduction matrix and README link | complete |

## M38 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M38A | Audit ROS 2 workflow hardening path | complete |
| M38B | Add local ROS 2 workspace smoke-check script | complete |
| M38C | Add report, reproduction entry, checker, and commit | in progress |

## M39 blocks

| Block | Purpose | Status |
| ----- | ------- | ------ |
| M39A | Audit ROS 2 replay node runtime interface | complete |
| M39B | Add and run ROS 2 end-to-end topic smoke script | complete |
| M39C | Add report, reproduction entry, checker, and commit | in progress |

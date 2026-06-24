# C++ Tracking Core

This report documents the small C++ tracking core added to the benchmark.

## Purpose

The Python pipeline orchestrates experiments, metrics, plots, reports, and ROS 2 replay. The C++ module demonstrates how latency-critical tracking primitives can be implemented in a compiled robotics-software style.

This is not a replacement for the Python benchmark. It is a compact systems-oriented core for association, track state, and risk scoring.

## Location

- `cpp/tracking_core/`

## Implemented components

### IoU and association

- `tracking_core::Box`
- `tracking_core::area`
- `tracking_core::iou`
- `tracking_core::greedy_associate`

The association function greedily matches detections to existing tracks by IoU threshold.

### Track lifecycle

- `TrackLifecycle::Tentative`
- `TrackLifecycle::Confirmed`
- `TrackLifecycle::Lost`
- `TrackLifecycle::Deleted`

The `TrackState` struct tracks:

- ID
- box
- age
- hits
- misses
- center position
- center velocity
- lifecycle state

### Risk scoring

The C++ risk core mirrors the deterministic risk-scoring idea used in the Python analysis:

- low-confidence risk
- small-box risk
- border risk
- motion-jump risk
- short-track risk

It also exposes:

- `risk_level`
- `safety_state`

## Tests

Run:

    bash scripts/check_cpp_tracking_core.sh

The check script:

- configures the CMake project
- builds the C++ library
- runs CTest
- runs the microbenchmark

## Latest local result

The C++ tracking core passed local build and tests.

Observed microbenchmark result:

- 128 detections
- 128 tracks
- 1000 iterations
- per-iteration time around `0.052 ms`

## Claim boundary

This C++ module is a compact tracking/risk core demonstration. It does not replace the full Python/Ultralytics/ByteTrack pipeline. It exists to show latency-critical robotics tracking primitives implemented and tested in C++.

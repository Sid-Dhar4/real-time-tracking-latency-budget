# Track Reliability Risk Diagnostics

This report adds a deterministic track-level reliability diagnostic for the KITTI tracking benchmark.

The goal is not to claim a learned safety model. The goal is to rank tracks by simple risk signals that are useful for robotics perception monitoring and debugging.

## Risk signals

Each per-frame track observation receives normalized risk components:

- low confidence risk
- small box risk
- image border / truncation risk
- frame-to-frame center jump risk
- short track risk

The final `risk_score` is a weighted combination of these components.

## Outputs

- `results/tables/m33_frame_risk_scores.csv`
- `results/tables/m33_track_risk_summary.csv`
- `results/tables/m33_top_risky_tracks.csv`

## Sequence analyzed

KITTI tracking sequence `0001`, using saved YOLOv8n + ByteTrack output.

## Summary

The sequence contains 2,514 tracked-object rows across 447 frames and 149 unique track IDs.

The top-ranked risky tracks are mostly short-lived, low-confidence, small-box, or border-adjacent tracks. This matches the intended diagnostic purpose: highlight tracks that are likely to be unstable or less reliable for robot-facing downstream consumers.

## Top risky tracks

See:

- `results/tables/m33_top_risky_tracks.csv`

The highest-risk track in this run is `track_id=1087`, with mean risk score approximately `0.651`.

## Caveats

- This is a deterministic diagnostic heuristic, not a learned uncertainty model.
- It does not prove causal failure by itself.
- It is intended to prioritize debugging and monitoring of potentially unstable tracks.
- A stronger future version could correlate risk scores with ID switches, false negatives, occlusion, or planner interventions.

# Track Risk Validation

This report validates that the deterministic track reliability score behaves in the intended direction.

## Question

Do higher-risk tracks look less reliable than lower-risk tracks?

The validation groups tracks into `low`, `medium`, and `high` risk buckets and compares:

- track lifetime
- mean confidence
- box area
- border-risk fraction
- motion-jump risk
- short-track risk
- final mean risk score

## Inputs

- `results/tables/m33_track_risk_summary.csv`

## Outputs

- `results/tables/m34_risk_bucket_summary.csv`
- `results/plots/m34_risk_bucket_summary.png`

## Result

The risk buckets behave as expected:

- high-risk tracks are shortest-lived
- high/medium-risk tracks have lower confidence than low-risk tracks
- medium/high-risk buckets have larger short-track risk
- the mean risk score increases from low to medium to high

In the analyzed sequence, the single high-risk track has one frame and mean confidence around `0.359`, while low-risk tracks average about `18.9` frames and mean confidence around `0.627`.

## Interpretation

This does not prove causal failure or learned uncertainty. It validates that the heuristic score is directionally meaningful for prioritizing unstable tracks for debugging and robot-facing diagnostics.

## Caveats

- This validation uses one KITTI sequence.
- The risk score is deterministic and hand-designed.
- Future work could correlate risk score directly with ID switches, false negatives, occlusion labels, or planner interventions.

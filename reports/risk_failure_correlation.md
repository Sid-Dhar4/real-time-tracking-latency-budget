# Risk vs Failure Correlation

This report compares deterministic track-risk scores against local tracking failure diagnostics.

## Purpose

The earlier risk validation showed that higher-risk tracks were shorter-lived and lower-confidence. This report goes further by comparing risk buckets against local failure signals:

- ID-switch-associated tracks
- false-positive-like unmatched detections
- false-negative frame burden
- track fragmentation and short-track rates

## Claim boundary

This is a local diagnostic analysis, not a public KITTI leaderboard result and not official TrackEval failure attribution. Matching is performed with local greedy IoU association against KITTI training labels for sequence `0001`.

The goal is to test whether the risk score is directionally useful for debugging and downstream robot-facing diagnostics.

## Headline findings

### Supported finding: risk aligns strongly with fragmentation

Higher-risk tracks are much more likely to be short-lived or fragmented.

- Low-risk short-track rate: `0.130`
- Medium-risk short-track rate: `0.778`
- High-risk short-track rate: `1.000`

This is the strongest result because the risk score intentionally includes short-track and stability-related components.

### Supported finding: frame-level risk burden increases with FP/FN burden

Frames in the high-risk bucket have higher false-negative and false-positive burden than frames in the low-risk bucket.

- Low-risk mean FN/frame: `1.923`
- High-risk mean FN/frame: `2.408`
- Low-risk FP-frame rate: `0.538`
- High-risk FP-frame rate: `0.789`

This supports using aggregate risk as a robot-facing diagnostic signal for perception reliability.

### Non-supported finding: risk does not predict ID switches here

ID switches do not increase monotonically with the current risk score.

- Low-risk ID-switch track rate: `0.348`
- High-risk ID-switch track rate: `0.000`

This likely happens because ID switches require a track to survive long enough to switch identity. Very short high-risk tracks can disappear before accumulating ID-switch events. Therefore, ID switches should be treated as a separate identity-consistency failure mode, not as a direct output of this risk score.

## Risk vs ID switches

| risk_level   |   track_count |   mean_risk_score |   mean_frames |   tracks_with_id_switch |   total_id_switch_events |   id_switch_track_rate |
|:-------------|--------------:|------------------:|--------------:|------------------------:|-------------------------:|-----------------------:|
| low          |           115 |            0.3635 |       19.6435 |                      40 |                       48 |                 0.3478 |
| medium       |            18 |            0.527  |        2.2222 |                       1 |                        1 |                 0.0556 |
| high         |             1 |            0.6507 |        1      |                       0 |                        0 |                 0      |

## Risk vs track fragmentation

| risk_level   |   track_count |   mean_risk_score |   mean_frames |   median_frames |   short_tracks |   fragmented_tracks |   mean_gap_count |   short_track_rate |   fragmented_track_rate |
|:-------------|--------------:|------------------:|--------------:|----------------:|---------------:|--------------------:|-----------------:|-------------------:|------------------------:|
| low          |           115 |            0.3635 |       19.6435 |              18 |             15 |                  61 |           3.6957 |             0.1304 |                  0.5304 |
| medium       |            18 |            0.527  |        2.2222 |               2 |             14 |                  16 |           4.0556 |             0.7778 |                  0.8889 |
| high         |             1 |            0.6507 |        1      |               1 |              1 |                   1 |           0      |             1      |                  1      |

## Frame risk burden vs false negatives / false positives

| risk_bucket   |   frame_count |   mean_max_risk_score |   mean_risk_score |   total_fn |   total_fp |   total_id_switches |   mean_fn_per_frame |   mean_fp_per_frame |   frames_with_fn |   frames_with_fp |   fn_frame_rate |   fp_frame_rate |
|:--------------|--------------:|----------------------:|------------------:|-----------:|-----------:|--------------------:|--------------------:|--------------------:|-----------------:|-----------------:|----------------:|----------------:|
| low           |           143 |                0.3601 |            0.3254 |        275 |        131 |                  13 |              1.9231 |              0.9161 |              105 |               77 |          0.7343 |          0.5385 |
| medium        |           142 |                0.4201 |            0.3517 |        305 |        196 |                  19 |              2.1479 |              1.3803 |              105 |               99 |          0.7394 |          0.6972 |
| high          |           142 |                0.498  |            0.3664 |        342 |        214 |                  17 |              2.4085 |              1.507  |              121 |              112 |          0.8521 |          0.7887 |

## Interpretation

The risk score is useful as a reliability diagnostic for short-lived, fragmented, unstable, or frame-level noisy tracking behavior.

It should not be oversold as a universal failure predictor. In this sequence, it is strongest for fragmentation and frame-level FP/FN burden, while ID switches remain better interpreted as a long-track identity-consistency issue.

## Outputs

- `results/tables/m43_risk_vs_id_switches.csv`
- `results/tables/m43_risk_vs_false_negatives.csv`
- `results/tables/m43_risk_vs_track_fragmentation.csv`
- `results/tables/m43_track_failure_diagnostics.csv`
- `results/tables/m43_frame_failure_diagnostics.csv`
- `results/plots/m43_risk_vs_failure_rate.png`

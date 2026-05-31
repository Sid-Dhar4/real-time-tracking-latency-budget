# Failure Analysis

## Scope

This report analyzes YOLOv8n + ByteTrack on KITTI tracking sequence `0000` for class `Car`.

These are local KITTI-style diagnostics, not official KITTI leaderboard results and not TrackEval HOTA.

## Selected threshold

- Selected confidence threshold: `0.65`
- Selection rule: best IDF1-like score from the M5 confidence sweep.
- Tracks CSV: `results/tracks/sweeps/yolov8n_bytetrack_seq0000_conf_0_65_tracks.csv`

## Aggregate failure counts

- False positives: `121`
- Missed GT boxes / false negatives: `135`
- ID switches: `2`

## Worst frames

| Frame | GT | Pred | TP | FP | FN | ID switches | Failure score |
| ----- | -- | ---- | -- | -- | -- | ----------- | ------------- |
| 148 | 7 | 6 | 4 | 2 | 3 | 1 | 8 |
| 131 | 7 | 4 | 3 | 1 | 4 | 1 | 8 |
| 146 | 7 | 5 | 3 | 2 | 4 | 0 | 6 |
| 147 | 7 | 5 | 3 | 2 | 4 | 0 | 6 |
| 150 | 7 | 5 | 3 | 2 | 4 | 0 | 6 |
| 151 | 7 | 5 | 3 | 2 | 4 | 0 | 6 |

## Failure-case images

- `results/failure_cases/m6_frame_000148_fp2_fn3_idsw1.jpg`
- `results/failure_cases/m6_frame_000131_fp1_fn4_idsw1.jpg`
- `results/failure_cases/m6_frame_000146_fp2_fn4_idsw0.jpg`
- `results/failure_cases/m6_frame_000147_fp2_fn4_idsw0.jpg`
- `results/failure_cases/m6_frame_000150_fp2_fn4_idsw0.jpg`
- `results/failure_cases/m6_frame_000151_fp2_fn4_idsw0.jpg`

## Interpretation

- Higher confidence reduced false positives and ID switches compared with the low-threshold baseline.
- The selected threshold still misses several ground-truth cars, especially where objects are small, partly occluded, or visually ambiguous.
- False positives remain important because a robot/autonomy stack may treat phantom tracks as obstacles.
- ID switches matter because downstream prediction/planning modules rely on stable object identity over time.

## Next improvements

- Compare threshold `0.50` vs `0.65` depending on whether recall or identity stability matters more.
- Add TrackEval/HOTA after export formatting is complete.
- Add per-class evaluation for Pedestrian after the Car pipeline is stable.
- Fix GPU driver before making final runtime claims.

## ID switch events

| Frame | GT track | Previous pred ID | New pred ID | IoU |
| ----- | -------- | ---------------- | ----------- | --- |
| 131 | 7 | 1114 | 1117 | 0.763 |
| 148 | 13 | 1124 | 1114 | 0.786 |

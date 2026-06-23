# Six-Sequence TrackEval KITTI Benchmark

Native TrackEval KITTI 2D box evaluation was run for class `car` on KITTI tracking sequences `0000` through `0005`.

## Combined results

- HOTA: `46.634`
- MOTA: `50.354`
- IDF1: `61.903`
- GT detections: `5793`
- Tracker detections: `3780`
- ID switches: `121`

## Per-sequence results

| sequence | HOTA | MOTA | IDF1 | IDSW | Dets | GT Dets |
| -------- | ---- | ---- | ---- | ---- | ---- | ------- |
| 0000 | 43.489 | 25.581 | 51.084 | 7 | 200 | 215 |
| 0001 | 50.009 | 54.842 | 70.177 | 35 | 1735 | 2272 |
| 0002 | 25.918 | 22.700 | 35.016 | 9 | 268 | 1000 |
| 0003 | 56.241 | 59.281 | 73.077 | 4 | 238 | 334 |
| 0004 | 36.823 | 56.641 | 42.249 | 34 | 477 | 768 |
| 0005 | 54.572 | 62.791 | 73.282 | 32 | 862 | 1204 |

## Notes

- This is a local TrackEval evaluation on KITTI training sequences, not a public KITTI leaderboard submission.
- The detector uses pretrained YOLOv8n weights.
- This expands benchmark coverage from 2 sequences to 6 sequences.

## Artifacts

- `results/tables/m21_trackeval_6seq_summary.csv`
- `results/plots/m21_trackeval_6seq_metrics.png`
- `results/trackeval_6seq/m21_car_summary.txt`
- `results/trackeval_6seq/m21_car_detailed.csv`

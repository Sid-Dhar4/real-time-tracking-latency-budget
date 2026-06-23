# TrackEval Dropped-Frame Stress Test

This stress test simulates intermittent perception output by removing tracker detections from every Nth frame before running native TrackEval KITTI evaluation for class `car`.

## Combined TrackEval results

| variant | HOTA | MOTA | IDF1 | DetRe | DetPr | IDSW | FN | FP | Dets |
| ------- | ---- | ---- | ---- | ----- | ----- | ---- | -- | -- | ---- |
| baseline | 49.412 | 52.312 | 68.385 | 51.002 | 65.551 | 42 | 848 | 296 | 1935 |
| drop_every_5 | 39.974 | 41.496 | 59.737 | 40.656 | 65.486 | 42 | 1178 | 235 | 1544 |
| drop_every_3 | 33.765 | 34.700 | 53.454 | 33.852 | 65.928 | 38 | 1398 | 188 | 1277 |
| drop_every_2 | 25.852 | 25.613 | 43.846 | 25.567 | 65.822 | 39 | 1666 | 145 | 966 |

## Interpretation

- HOTA, MOTA, and IDF1 degrade monotonically as more frames are dropped.
- The largest damage is recall-driven: false negatives rise as detections are removed.
- This shows the tracker is sensitive to intermittent detector availability, which is relevant for robotics perception under compute limits, motion blur, dropped frames, and sensor/latency failures.

## Artifacts

- `results/tables/m14_trackeval_stress_summary.csv`
- `results/tables/m14_stress_export_summary.csv`
- `results/plots/m14_trackeval_stress_metrics.png`
- `results/trackeval_stress/m14_*_car_summary.txt`


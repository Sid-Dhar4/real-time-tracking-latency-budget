# Tracker Comparison: ByteTrack vs Simple IoU Tracker

This comparison evaluates two trackers using the same YOLOv8n detections, KITTI tracking sequences `0000` and `0001`, native TrackEval KITTI 2D box evaluation, and class `car`.

## Combined TrackEval results

| tracker | HOTA | MOTA | IDF1 | IDSW | FN | FP | Dets | IDs |
| ------- | ---- | ---- | ---- | ---- | -- | -- | ---- | --- |
| bytetrack | 49.412 | 52.312 | 68.385 | 42 | 848 | 296 | 1935 | 135 |
| iou_tracker | 48.814 | 45.879 | 58.949 | 197 | 444 | 705 | 2748 | 436 |

## Interpretation

- The simple IoU tracker has higher recall because it keeps more detections.
- The simple IoU tracker creates far more identity fragmentation: `436` predicted IDs versus `135` for ByteTrack.
- ByteTrack has much stronger identity consistency: `IDF1 68.385` versus `58.949`, and `IDSW 42` versus `197`.
- ByteTrack also has higher MOTA because it produces fewer false positives and ID switches.

## Artifacts

- `results/tables/m15_tracker_comparison.csv`
- `results/plots/m15_tracker_comparison_metrics.png`
- `results/trackeval_comparison/m15_bytetrack_car_summary.txt`
- `results/trackeval_comparison/m15_iou_tracker_car_summary.txt`
- `results/tracks/yolov8n_iou_seq0000_tracks.csv`
- `results/tracks/yolov8n_iou_seq0001_tracks.csv`


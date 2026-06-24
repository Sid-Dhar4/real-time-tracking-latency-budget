# Resume Bullets

## Use now

- Built a reproducible KITTI tracking-by-detection benchmark using YOLOv8n and ByteTrack, exporting tracks and measuring local KITTI-style precision/recall, IDF1-like, MOTA-like, ID switches, false positives, false negatives, and CPU latency.

- Swept detector confidence thresholds on KITTI sequence `0000`, reducing false positives from `357` to `121` and ID switches from `11` to `2` while improving local IDF1-like score from `0.310` to `0.441`; generated failure-case visualizations for missed detections, false positives, and ID switches.

## Stronger version after TrackEval/multi-sequence extension

- Built a reproducible KITTI multi-object tracking benchmark using YOLOv8n and ByteTrack/OC-SORT, reporting standard tracking metrics, latency distributions, multi-sequence threshold ablations, and failure timelines for ID switches, false positives, and missed detections.

## Do not claim yet

- Public KITTI test-server result
- TrackEval HOTA
- GPU real-time performance
- Production-ready autonomous driving system
- Trained detector

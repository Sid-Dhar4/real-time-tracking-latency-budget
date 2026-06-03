# Interview Notes

## 30-second explanation

I built a tracking-by-detection benchmark on KITTI using YOLOv8n and ByteTrack. The project runs detector and tracker inference, exports tracks, computes local KITTI-style metrics, measures CPU latency, sweeps confidence thresholds, and analyzes false positives, missed detections, and ID switches. The goal was to show robotics perception tradeoffs under runtime constraints, not just run a YOLO demo.

## 2-minute explanation

The pipeline starts with KITTI tracking frames from sequence `0000`. YOLOv8n produces 2D detections, ByteTrack associates detections over time, and the system exports track IDs to CSV. I wrote a local KITTI-style evaluator for the Car class using IoU matching, then computed precision, recall, false positives, false negatives, ID switches, MOTA-like, and IDF1-like metrics.

The key result came from sweeping detector confidence thresholds. At confidence `0.25`, the system had more recall but produced `357` false positives and `11` ID switches. At confidence `0.65`, false positives dropped to `121` and ID switches dropped to `2`, with the best local IDF1-like score of `0.441`. The tradeoff was lower recall.

## Questions to prepare

### Why YOLOv8n?

Because the MVP goal was a reliable, latency-aware benchmark. A small detector makes runtime tradeoffs visible and keeps setup simple.

### Why ByteTrack?

ByteTrack is a practical tracking-by-detection baseline that associates detections across frames and gives object IDs over time.

### Why did higher confidence improve IDF1-like?

Higher confidence removed low-quality detections that became false positives or unstable tracks. That improved identity consistency, but it also reduced recall.

### Why is MOTA-like negative?

The local MOTA-like score penalizes false positives, false negatives, and ID switches relative to the number of ground-truth objects. If the total error count exceeds the GT count, the score can go negative. That is a warning about false positives, not a bug.

### What would you improve next?

I would integrate TrackEval/HOTA, evaluate more KITTI sequences, compare ByteTrack with OC-SORT, add a warmup-aware latency benchmark, fix the NVIDIA driver for GPU latency, and add per-class Pedestrian analysis.

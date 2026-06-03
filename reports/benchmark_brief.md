# Benchmark Brief

## Project

Real-Time Object Tracking Under a Robotics Latency Budget

## One-sentence summary

Built a KITTI tracking-by-detection benchmark using YOLOv8n and ByteTrack, measured local tracking quality and CPU latency, swept confidence thresholds, and analyzed false positives, missed detections, and ID switches.

## Current MVP result

Best local IDF1-like threshold: `0.65`.

Compared with confidence `0.25`:

- False positives: `357` -> `121`
- ID switches: `11` -> `2`
- IDF1-like: `0.310` -> `0.441`
- Recall: `0.613` -> `0.444`

## Interpretation

The confidence threshold sweep showed that tracking quality is not only about model choice. A simple threshold change materially changed false positives, identity stability, recall, and latency.

Lower thresholds preserved more detections but created more noisy tracks. Higher thresholds reduced false positives and ID switches but missed more ground-truth cars.

## Next extensions

1. TrackEval/HOTA integration.
2. Multi-sequence evaluation.
3. ByteTrack vs OC-SORT comparison.
4. Warmup-aware latency benchmark.
5. GPU rerun after NVIDIA driver fix.

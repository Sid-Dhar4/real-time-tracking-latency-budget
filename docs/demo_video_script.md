# Demo Video Script

## 30-second demo

I built a KITTI tracking-by-detection benchmark using YOLOv8n and ByteTrack. It measures local tracking quality, CPU latency, threshold tradeoffs, and failure cases.

The key result is that increasing confidence from `0.25` to `0.65` reduced false positives from `357` to `121` and ID switches from `11` to `2`, while improving local IDF1-like from `0.310` to `0.441`.

Important caveat: these are local KITTI-style metrics, not official TrackEval/HOTA or KITTI leaderboard results.

# Demo Video Script

## 30-second demo

I built a KITTI tracking-by-detection benchmark using YOLOv8n and ByteTrack. It measures local tracking quality, CPU latency, threshold tradeoffs, and failure cases.

The key result is that increasing confidence from `0.25` to `0.65` reduced false positives from `357` to `121` and ID switches from `11` to `2`, while improving local IDF1-like from `0.310` to `0.441`.

Important caveat: the demo video is a qualitative overlay; primary TrackEval results are reported separately in `reports/trackeval_6seq_results.md` and are not a public KITTI leaderboard submission.

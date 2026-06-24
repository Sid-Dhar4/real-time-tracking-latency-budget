# Limitations

- Primary metrics are local TrackEval evaluations on KITTI training sequences, not a public KITTI leaderboard submission.
- Some older diagnostic tables use local KITTI-style metrics for debugging and are clearly labeled as diagnostic.
- No TrackEval/HOTA yet.
- CPU runtime only because `nvidia-smi` was not working.
- Pretrained YOLOv8n, not KITTI-trained.
- First MVP uses only KITTI sequence `0000`.
- ByteTrack is integrated through Ultralytics for reliability.

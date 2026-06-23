# Demo Notes

## Artifact

- Video: `results/videos/m11_seq0001_demo_overlay.mp4`
- Frame: `results/plots/m11_seq0001_demo_frame.jpg`

## What it shows

This demo overlays YOLOv8n + ByteTrack outputs on KITTI tracking sequence `0001`.

The overlay includes:

- bounding boxes
- track IDs
- class names
- confidence scores
- frame number
- per-frame tracker latency
- approximate FPS from latency

## Caveat

This is a CPU benchmark artifact and not a GPU runtime claim.

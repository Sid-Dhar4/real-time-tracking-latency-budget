
#!/usr/bin/env python3

from pathlib import Path
import argparse
import cv2
import pandas as pd


def draw_label(img, text, x, y, scale=0.55, thickness=1):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", default="0001")
    ap.add_argument("--image-dir", default="data/kitti_tracking/training/image_02/0001")
    ap.add_argument("--tracks-csv", default="results/tracks/yolov8n_bytetrack_seq0001_tracks.csv")
    ap.add_argument("--output-video", default="results/videos/m11_seq0001_demo_overlay.mp4")
    ap.add_argument("--output-frame", default="results/plots/m11_seq0001_demo_frame.jpg")
    ap.add_argument("--start-frame", type=int, default=0)
    ap.add_argument("--max-frames", type=int, default=160)
    ap.add_argument("--fps", type=int, default=12)
    args = ap.parse_args()

    image_dir = Path(args.image_dir)
    tracks = pd.read_csv(args.tracks_csv)
    tracks["frame"] = tracks["frame"].astype(int)

    frame_ids = sorted(tracks["frame"].unique())
    frame_ids = [f for f in frame_ids if f >= args.start_frame][: args.max_frames]
    if not frame_ids:
        raise RuntimeError("No frames found for demo.")

    first_img = cv2.imread(str(image_dir / f"{frame_ids[0]:06d}.png"))
    if first_img is None:
        raise RuntimeError("Could not read first image.")
    h, w = first_img.shape[:2]

    out_video = Path(args.output_video)
    out_frame = Path(args.output_frame)
    out_video.parent.mkdir(parents=True, exist_ok=True)
    out_frame.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(str(out_video), cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer: {out_video}")

    saved_frame = False

    for local_idx, frame in enumerate(frame_ids):
        img_path = image_dir / f"{frame:06d}.png"
        img = cv2.imread(str(img_path))
        if img is None:
            continue

        rows = tracks[tracks["frame"] == frame].copy()
        latency = float(rows["latency_ms"].iloc[0]) if len(rows) else 0.0

        for _, r in rows.iterrows():
            x1, y1, x2, y2 = map(int, [r.x1, r.y1, r.x2, r.y2])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
            label = f"ID {int(r.track_id)} {r.class_name} {float(r.confidence):.2f}"
            draw_label(img, label, x1, max(18, y1 - 5), 0.45, 1)

        overlay = [
            "YOLOv8n + ByteTrack",
            f"KITTI seq {args.sequence} | frame {frame:06d}",
            f"tracks: {len(rows)} | latency: {latency:.2f} ms | approx FPS: {1000.0/latency:.1f}" if latency > 0 else f"tracks: {len(rows)}",
            "CPU run | local benchmark artifact",
        ]

        y = 28
        for line in overlay:
            draw_label(img, line, 18, y, 0.65, 1)
            y += 28

        writer.write(img)

        if not saved_frame and local_idx >= min(30, len(frame_ids)-1):
            cv2.imwrite(str(out_frame), img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            saved_frame = True

    writer.release()

    print(f"wrote_video: {out_video}")
    print(f"wrote_frame: {out_frame}")
    print(f"frames_written: {len(frame_ids)}")


if __name__ == "__main__":
    main()

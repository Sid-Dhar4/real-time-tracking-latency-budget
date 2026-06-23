#!/usr/bin/env python3

import argparse
import csv
import time
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


def load_tracks_csv(path):
    rows = []
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def group_by_frame(rows):
    frames = {}
    for row in rows:
        frame = int(float(row["frame"]))
        frames.setdefault(frame, []).append(row)
    return frames


def draw_tracks(image, rows, sequence, frame):
    out = image.copy()

    cv2.putText(
        out,
        f"KITTI seq {sequence} frame {frame:06d} | tracks: {len(rows)}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    for row in rows:
        x1 = int(float(row["x1"]))
        y1 = int(float(row["y1"]))
        x2 = int(float(row["x2"]))
        y2 = int(float(row["y2"]))
        track_id = int(float(row["track_id"]))
        conf = float(row["confidence"])
        cls = str(row["class_name"])

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{cls} id={track_id} {conf:.2f}"
        cv2.putText(
            out,
            label,
            (x1, max(15, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    return out


class KittiDebugImageReplayNode(Node):
    def __init__(self, tracks_csv, image_dir, sequence, fps, max_frames, frame_id):
        super().__init__("kitti_debug_image_replay")

        self.tracks_csv = Path(tracks_csv)
        self.image_dir = Path(image_dir)
        self.sequence = str(sequence).zfill(4)
        self.fps = float(fps)
        self.max_frames = int(max_frames)
        self.frame_id = str(frame_id)

        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, "/tracking/debug_image", 10)

        self.rows = load_tracks_csv(self.tracks_csv)
        self.frames_to_rows = group_by_frame(self.rows)
        self.frames = sorted(self.frames_to_rows.keys())
        if self.max_frames > 0:
            self.frames = self.frames[: self.max_frames]

        self.idx = 0
        period = 1.0 / self.fps if self.fps > 0 else 0.1
        self.timer = self.create_timer(period, self.tick)

        self.get_logger().info(f"Loaded {len(self.rows)} track rows from {self.tracks_csv}")
        self.get_logger().info(f"Using images from {self.image_dir}")
        self.get_logger().info(f"Publishing /tracking/debug_image for {len(self.frames)} frames")

    def tick(self):
        if self.idx >= len(self.frames):
            self.get_logger().info("Debug image replay complete.")
            rclpy.shutdown()
            return

        frame = int(self.frames[self.idx])
        rows = self.frames_to_rows.get(frame, [])
        image_name = rows[0].get("image_name", f"{frame:06d}.png") if rows else f"{frame:06d}.png"
        image_path = self.image_dir / image_name

        image = cv2.imread(str(image_path))
        if image is None:
            self.get_logger().warning(f"Could not read image: {image_path}")
            self.idx += 1
            return

        t0 = time.perf_counter()
        debug = draw_tracks(image, rows, self.sequence, frame)
        msg = self.bridge.cv2_to_imgmsg(debug, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        self.pub.publish(msg)
        publish_ms = (time.perf_counter() - t0) * 1000.0

        if self.idx < 3:
            self.get_logger().info(f"published frame={frame} tracks={len(rows)} publish_ms={publish_ms:.3f}")

        self.idx += 1


def dry_run(tracks_csv, image_dir, sequence, max_frames):
    rows = load_tracks_csv(tracks_csv)
    frames_to_rows = group_by_frame(rows)
    frames = sorted(frames_to_rows.keys())
    if max_frames > 0:
        frames = frames[:max_frames]

    print("tracks_csv:", tracks_csv)
    print("image_dir:", image_dir)
    print("sequence:", str(sequence).zfill(4))
    print("rows:", len(rows))
    print("frames:", len(frames))

    for frame in frames[:3]:
        rows_for_frame = frames_to_rows.get(frame, [])
        image_name = rows_for_frame[0].get("image_name", f"{frame:06d}.png") if rows_for_frame else f"{frame:06d}.png"
        image_path = Path(image_dir) / image_name
        img = cv2.imread(str(image_path))
        print("frame", frame, "tracks", len(rows_for_frame), "image", image_path, "loaded", img is not None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracks-csv", default="results/tracks/yolov8n_bytetrack_seq0001_tracks.csv")
    parser.add_argument("--image-dir", default="data/kitti_tracking/training/image_02/0001")
    parser.add_argument("--sequence", default="0001")
    parser.add_argument("--fps", type=float, default=10.0)
    parser.add_argument("--max-frames", type=int, default=50)
    parser.add_argument("--frame-id", default="kitti_camera")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        dry_run(args.tracks_csv, args.image_dir, args.sequence, args.max_frames)
        return

    rclpy.init()
    node = KittiDebugImageReplayNode(
        args.tracks_csv,
        args.image_dir,
        args.sequence,
        args.fps,
        args.max_frames,
        args.frame_id,
    )
    rclpy.spin(node)


if __name__ == "__main__":
    main()

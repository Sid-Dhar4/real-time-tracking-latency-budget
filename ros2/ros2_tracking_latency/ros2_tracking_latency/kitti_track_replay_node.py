#!/usr/bin/env python3

import argparse
import csv
import json
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def load_tracks_csv(path):
    rows = []
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def group_tracks_by_frame(rows):
    frames = {}
    for r in rows:
        frame = int(float(r["frame"]))
        frames.setdefault(frame, []).append(r)
    return frames


def row_to_object(r):
    return {
        "track_id": int(float(r["track_id"])),
        "class_name": str(r["class_name"]),
        "confidence": float(r["confidence"]),
        "bbox_xyxy": [
            float(r["x1"]),
            float(r["y1"]),
            float(r["x2"]),
            float(r["y2"]),
        ],
    }


class KittiTrackReplayNode(Node):
    def __init__(self, tracks_csv, sequence, fps, max_frames):
        super().__init__("kitti_track_replay")
        self.tracks_csv = Path(tracks_csv)
        self.sequence = str(sequence).zfill(4)
        self.fps = float(fps)
        self.max_frames = int(max_frames)

        self.objects_pub = self.create_publisher(String, "/tracking/objects", 10)
        self.status_pub = self.create_publisher(String, "/tracking/status", 10)

        self.rows = load_tracks_csv(self.tracks_csv)
        self.frames_to_rows = group_tracks_by_frame(self.rows)
        self.frames = sorted(self.frames_to_rows.keys())
        if self.max_frames > 0:
            self.frames = self.frames[: self.max_frames]
        self.idx = 0

        period = 1.0 / self.fps if self.fps > 0 else 0.1
        self.timer = self.create_timer(period, self.tick)

        self.get_logger().info("Loaded {} rows from {}".format(len(self.rows), self.tracks_csv))
        self.get_logger().info("Replaying {} frames for sequence {} at {} FPS".format(len(self.frames), self.sequence, self.fps))

    def tick(self):
        if self.idx >= len(self.frames):
            self.get_logger().info("Replay complete.")
            rclpy.shutdown()
            return

        frame = int(self.frames[self.idx])
        t0 = time.perf_counter()
        rows = self.frames_to_rows.get(frame, [])
        objects = [row_to_object(r) for r in rows]
        publish_latency_ms = (time.perf_counter() - t0) * 1000.0

        payload = {
            "sequence": self.sequence,
            "frame": frame,
            "num_tracks": len(objects),
            "objects": objects,
        }
        status = {
            "sequence": self.sequence,
            "frame": frame,
            "num_tracks": len(objects),
            "fps": self.fps,
            "publish_latency_ms": publish_latency_ms,
            "source_csv": str(self.tracks_csv),
        }

        msg = String()
        msg.data = json.dumps(payload)
        self.objects_pub.publish(msg)

        status_msg = String()
        status_msg.data = json.dumps(status)
        self.status_pub.publish(status_msg)

        self.idx += 1


def dry_run(tracks_csv, sequence, max_frames):
    rows = load_tracks_csv(tracks_csv)
    frames_to_rows = group_tracks_by_frame(rows)
    frames = sorted(frames_to_rows.keys())
    if max_frames > 0:
        frames = frames[:max_frames]
    print("dry_run_tracks_csv:", tracks_csv)
    print("sequence:", str(sequence).zfill(4))
    print("rows:", len(rows))
    print("frames:", len(frames))
    for frame in frames[:3]:
        print("frame", int(frame), "num_tracks", len(frames_to_rows.get(frame, [])))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracks-csv", default="results/tracks/yolov8n_bytetrack_seq0001_tracks.csv")
    parser.add_argument("--sequence", default="0001")
    parser.add_argument("--fps", type=float, default=10.0)
    parser.add_argument("--max-frames", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        dry_run(args.tracks_csv, args.sequence, args.max_frames)
        return

    rclpy.init()
    node = KittiTrackReplayNode(args.tracks_csv, args.sequence, args.fps, args.max_frames)
    rclpy.spin(node)


if __name__ == "__main__":
    main()

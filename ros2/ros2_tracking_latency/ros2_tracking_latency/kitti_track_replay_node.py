#!/usr/bin/env python3

import argparse
import csv
import json
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose


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


def row_to_detection(r, stamp, frame_id):
    x1 = float(r["x1"])
    y1 = float(r["y1"])
    x2 = float(r["x2"])
    y2 = float(r["y2"])

    det = Detection2D()
    det.header.stamp = stamp
    det.header.frame_id = frame_id
    det.id = str(int(float(r["track_id"])))

    hyp = ObjectHypothesisWithPose()
    hyp.hypothesis.class_id = str(r["class_name"])
    hyp.hypothesis.score = float(r["confidence"])
    det.results.append(hyp)

    det.bbox.center.position.x = (x1 + x2) / 2.0
    det.bbox.center.position.y = (y1 + y2) / 2.0
    det.bbox.center.theta = 0.0
    det.bbox.size_x = max(0.0, x2 - x1)
    det.bbox.size_y = max(0.0, y2 - y1)

    return det


def rows_to_detection_array(rows, stamp, frame_id):
    msg = Detection2DArray()
    msg.header.stamp = stamp
    msg.header.frame_id = frame_id

    for r in rows:
        msg.detections.append(row_to_detection(r, stamp, frame_id))

    return msg


def make_diagnostic_array(status_values, stamp):
    msg = DiagnosticArray()
    msg.header.stamp = stamp
    msg.header.frame_id = "tracking_latency"

    diag = DiagnosticStatus()
    diag.level = DiagnosticStatus.OK if isinstance(DiagnosticStatus.OK, (bytes, bytearray)) else bytes([int(DiagnosticStatus.OK)])
    diag.name = "tracking_latency/kitti_track_replay"
    diag.message = "replaying saved KITTI tracking outputs"
    diag.hardware_id = "offline_kitti_tracks"

    for key, value in status_values.items():
        kv = KeyValue()
        kv.key = str(key)
        kv.value = str(value)
        diag.values.append(kv)

    msg.status.append(diag)
    return msg


class KittiTrackReplayNode(Node):
    def __init__(self, tracks_csv, sequence, fps, max_frames, frame_id):
        super().__init__("kitti_track_replay")
        self.tracks_csv = Path(tracks_csv)
        self.sequence = str(sequence).zfill(4)
        self.fps = float(fps)
        self.max_frames = int(max_frames)
        self.frame_id = str(frame_id)

        self.objects_pub = self.create_publisher(String, "/tracking/objects", 10)
        self.status_pub = self.create_publisher(String, "/tracking/status", 10)
        self.detections_pub = self.create_publisher(Detection2DArray, "/tracking/detections_2d", 10)
        self.diagnostics_pub = self.create_publisher(DiagnosticArray, "/tracking/diagnostics", 10)

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
        stamp = self.get_clock().now().to_msg()
        rows = self.frames_to_rows.get(frame, [])
        objects = [row_to_object(r) for r in rows]
        detections_msg = rows_to_detection_array(rows, stamp, self.frame_id)
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
        self.detections_pub.publish(detections_msg)
        self.diagnostics_pub.publish(make_diagnostic_array(status, stamp))

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
    parser.add_argument("--frame-id", default="kitti_camera")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        dry_run(args.tracks_csv, args.sequence, args.max_frames)
        return

    rclpy.init()
    node = KittiTrackReplayNode(args.tracks_csv, args.sequence, args.fps, args.max_frames, args.frame_id)
    rclpy.spin(node)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import argparse
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class Track:
    track_id: int
    detection: Detection
    last_frame: int
    hits: int = 1
    misses: int = 0


def box_area(box):
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def box_iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    inter = box_area((ix1, iy1, ix2, iy2))
    union = box_area(a) + box_area(b) - inter
    if union <= 0.0:
        return 0.0
    return inter / union


def image_to_gray(msg: Image):
    data = bytes(msg.data)

    if msg.encoding in ("mono8", "8UC1"):
        step = int(msg.step) if msg.step else int(msg.width)
        rows = []
        for y in range(int(msg.height)):
            start = y * step
            rows.append(list(data[start : start + int(msg.width)]))
        return rows

    if msg.encoding in ("rgb8", "bgr8"):
        step = int(msg.step) if msg.step else int(msg.width) * 3
        rows = []
        for y in range(int(msg.height)):
            row = []
            for x in range(int(msg.width)):
                offset = y * step + x * 3
                row.append(int((data[offset] + data[offset + 1] + data[offset + 2]) / 3))
            rows.append(row)
        return rows

    raise ValueError(f"Unsupported encoding for smoke-test online node: {msg.encoding}")


def detect_bright_regions(
    msg: Image,
    threshold: int,
    min_area: int,
    class_name: str,
) -> List[Detection]:
    gray = image_to_gray(msg)
    height = len(gray)
    width = len(gray[0]) if height else 0

    mask = [[gray[y][x] >= threshold for x in range(width)] for y in range(height)]
    visited = [[False for _ in range(width)] for _ in range(height)]

    detections: List[Detection] = []

    for y in range(height):
        for x0 in range(width):
            if visited[y][x0] or not mask[y][x0]:
                continue

            stack = [(int(x0), int(y))]
            visited[y][x0] = True
            min_x = max_x = int(x0)
            min_y = max_y = int(y)
            count = 0

            while stack:
                x, yy = stack.pop()
                count += 1
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, yy)
                max_y = max(max_y, yy)

                for nx, ny in ((x + 1, yy), (x - 1, yy), (x, yy + 1), (x, yy - 1)):
                    if nx < 0 or nx >= width or ny < 0 or ny >= height:
                        continue
                    if visited[ny][nx] or not mask[ny][nx]:
                        continue
                    visited[ny][nx] = True
                    stack.append((nx, ny))

            if count >= min_area:
                detections.append(
                    Detection(
                        class_id=0,
                        class_name=class_name,
                        confidence=1.0,
                        x1=float(min_x),
                        y1=float(min_y),
                        x2=float(max_x + 1),
                        y2=float(max_y + 1),
                    )
                )

    detections.sort(key=lambda d: (d.x1, d.y1))
    return detections


def detection_box(det: Detection):
    return (det.x1, det.y1, det.x2, det.y2)


def compute_risk(det: Detection, width: int, height: int, hits: int):
    area = box_area(detection_box(det))
    image_area = max(1.0, float(width * height))
    normalized_area = min(1.0, area / image_area)

    low_confidence_risk = max(0.0, min(1.0, 1.0 - det.confidence))
    small_box_risk = max(0.0, min(1.0, 1.0 - normalized_area * 20.0))

    margin = 4.0
    near_border = (
        det.x1 <= margin
        or det.y1 <= margin
        or det.x2 >= float(width) - margin
        or det.y2 >= float(height) - margin
    )
    border_risk = 1.0 if near_border else 0.0
    motion_jump_risk = 0.0
    short_track_risk = max(0.0, min(1.0, 1.0 / max(1, hits)))

    risk_score = (
        0.25 * low_confidence_risk
        + 0.20 * small_box_risk
        + 0.15 * border_risk
        + 0.25 * motion_jump_risk
        + 0.15 * short_track_risk
    )
    risk_score = max(0.0, min(1.0, risk_score))

    if risk_score >= 0.65:
        level = "high"
    elif risk_score >= 0.45:
        level = "medium"
    else:
        level = "low"

    return {
        "low_confidence_risk": low_confidence_risk,
        "small_box_risk": small_box_risk,
        "border_risk": border_risk,
        "motion_jump_risk": motion_jump_risk,
        "short_track_risk": short_track_risk,
        "risk_score": risk_score,
        "risk_level": level,
    }


def make_detection_array(detections: List[Detection], stamp, frame_id: str):
    msg = Detection2DArray()
    msg.header.stamp = stamp
    msg.header.frame_id = frame_id

    for det in detections:
        d = Detection2D()
        d.header.stamp = stamp
        d.header.frame_id = frame_id

        d.bbox.center.position.x = 0.5 * (det.x1 + det.x2)
        d.bbox.center.position.y = 0.5 * (det.y1 + det.y2)
        d.bbox.size_x = det.x2 - det.x1
        d.bbox.size_y = det.y2 - det.y1

        hyp = ObjectHypothesisWithPose()
        hyp.hypothesis.class_id = str(det.class_id)
        hyp.hypothesis.score = float(det.confidence)
        d.results.append(hyp)

        msg.detections.append(d)

    return msg


def make_diagnostics(status, stamp):
    arr = DiagnosticArray()
    arr.header.stamp = stamp
    arr.header.frame_id = "tracking_latency"

    diag = DiagnosticStatus()
    diag.name = "online_image_iou_tracking"
    diag.hardware_id = "ros2_tracking_latency"
    diag.level = DiagnosticStatus.OK
    diag.message = status.get("safety_state", "nominal")

    for key, value in status.items():
        diag.values.append(KeyValue(key=str(key), value=str(value)))

    arr.status.append(diag)
    return arr


class OnlineImageIouTrackingNode(Node):
    def __init__(
        self,
        image_topic: str,
        threshold: int,
        min_area: int,
        iou_threshold: float,
        max_age: int,
        class_name: str,
        frame_id: str,
    ):
        super().__init__("online_image_iou_tracking")

        self.threshold = int(threshold)
        self.min_area = int(min_area)
        self.iou_threshold = float(iou_threshold)
        self.max_age = int(max_age)
        self.class_name = str(class_name)
        self.frame_id = str(frame_id)

        self.frame_count = 0
        self.next_track_id = 1
        self.tracks: Dict[int, Track] = {}

        self.objects_pub = self.create_publisher(String, "/tracking/objects", 10)
        self.status_pub = self.create_publisher(String, "/tracking/status", 10)
        self.detections_pub = self.create_publisher(Detection2DArray, "/tracking/detections_2d", 10)
        self.diagnostics_pub = self.create_publisher(DiagnosticArray, "/tracking/diagnostics", 10)
        self.risk_pub = self.create_publisher(String, "/tracking/risk", 10)
        self.safety_pub = self.create_publisher(String, "/tracking/safety_status", 10)

        self.sub = self.create_subscription(Image, image_topic, self.on_image, 10)

        self.get_logger().info(
            f"Online image IoU tracker subscribed to {image_topic}, threshold={threshold}, min_area={min_area}"
        )

    def associate(self, detections: List[Detection]) -> List[Tuple[int, Detection]]:
        track_ids = list(self.tracks.keys())
        unmatched_tracks = set(track_ids)
        unmatched_detections = set(range(len(detections)))
        matches: List[Tuple[int, Detection]] = []

        candidates = []
        for tid in track_ids:
            track_box = detection_box(self.tracks[tid].detection)
            for det_i, det in enumerate(detections):
                score = box_iou(track_box, detection_box(det))
                if score >= self.iou_threshold:
                    candidates.append((score, tid, det_i))

        candidates.sort(reverse=True, key=lambda x: x[0])
        used_tracks = set()
        used_detections = set()

        for _, tid, det_i in candidates:
            if tid in used_tracks or det_i in used_detections:
                continue
            used_tracks.add(tid)
            used_detections.add(det_i)
            unmatched_tracks.discard(tid)
            unmatched_detections.discard(det_i)
            matches.append((tid, detections[det_i]))

        for det_i in sorted(unmatched_detections):
            tid = self.next_track_id
            self.next_track_id += 1
            matches.append((tid, detections[det_i]))

        for tid in list(unmatched_tracks):
            self.tracks[tid].misses += 1
            if self.tracks[tid].misses > self.max_age:
                self.tracks.pop(tid, None)

        return matches

    def on_image(self, msg: Image):
        start = time.perf_counter()
        stamp = self.get_clock().now().to_msg()

        detections = detect_bright_regions(
            msg,
            threshold=self.threshold,
            min_area=self.min_area,
            class_name=self.class_name,
        )

        matches = self.associate(detections)

        objects = []
        risk_entries = []

        for tid, det in matches:
            if tid in self.tracks:
                track = self.tracks[tid]
                track.detection = det
                track.last_frame = self.frame_count
                track.hits += 1
                track.misses = 0
            else:
                track = Track(track_id=tid, detection=det, last_frame=self.frame_count)
                self.tracks[tid] = track

            risk = compute_risk(det, msg.width, msg.height, track.hits)
            risk_entries.append({"track_id": tid, **risk})

            objects.append(
                {
                    "track_id": tid,
                    "class_name": det.class_name,
                    "confidence": det.confidence,
                    "x1": det.x1,
                    "y1": det.y1,
                    "x2": det.x2,
                    "y2": det.y2,
                    "risk_score": risk["risk_score"],
                    "risk_level": risk["risk_level"],
                    "hits": track.hits,
                }
            )

        risk_scores = [entry["risk_score"] for entry in risk_entries]
        max_risk = max(risk_scores) if risk_scores else 0.0
        mean_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        medium_or_high = sum(score >= 0.45 for score in risk_scores)
        high = sum(score >= 0.65 for score in risk_scores)

        if high > 0:
            safety_state = "degraded"
            reason = "one or more high-risk online tracks active"
        elif medium_or_high > 0:
            safety_state = "caution"
            reason = "one or more medium-risk online tracks active"
        else:
            safety_state = "nominal"
            reason = "all online tracks below medium-risk threshold"

        publish_latency_ms = (time.perf_counter() - start) * 1000.0

        payload = {
            "mode": "online_image_iou",
            "frame": self.frame_count,
            "num_tracks": len(objects),
            "objects": objects,
        }
        status = {
            "mode": "online_image_iou",
            "frame": self.frame_count,
            "num_tracks": len(objects),
            "num_active_tracks": len(self.tracks),
            "publish_latency_ms": publish_latency_ms,
            "safety_state": safety_state,
            "max_risk_score": max_risk,
            "mean_risk_score": mean_risk,
        }
        risk_payload = {
            "mode": "online_image_iou",
            "frame": self.frame_count,
            "num_risk_rows": len(risk_entries),
            "max_risk_score": max_risk,
            "mean_risk_score": mean_risk,
            "num_medium_or_high_risk_tracks": medium_or_high,
            "num_high_risk_tracks": high,
            "safety_state": safety_state,
            "reason": reason,
            "tracks": risk_entries,
        }
        safety_payload = {
            "mode": "online_image_iou",
            "frame": self.frame_count,
            "safety_state": safety_state,
            "reason": reason,
            "max_risk_score": max_risk,
            "num_medium_or_high_risk_tracks": medium_or_high,
        }

        objects_msg = String()
        objects_msg.data = json.dumps(payload)
        self.objects_pub.publish(objects_msg)

        status_msg = String()
        status_msg.data = json.dumps(status)
        self.status_pub.publish(status_msg)

        self.detections_pub.publish(make_detection_array(detections, stamp, self.frame_id))
        self.diagnostics_pub.publish(make_diagnostics(status, stamp))

        risk_msg = String()
        risk_msg.data = json.dumps(risk_payload)
        self.risk_pub.publish(risk_msg)

        safety_msg = String()
        safety_msg.data = json.dumps(safety_payload)
        self.safety_pub.publish(safety_msg)

        self.frame_count += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-topic", default="/camera/image_raw")
    parser.add_argument("--threshold", type=int, default=200)
    parser.add_argument("--min-area", type=int, default=80)
    parser.add_argument("--iou-threshold", type=float, default=0.3)
    parser.add_argument("--max-age", type=int, default=2)
    parser.add_argument("--class-name", default="bright_object")
    parser.add_argument("--frame-id", default="camera")
    args = parser.parse_args()

    rclpy.init()
    node = OnlineImageIouTrackingNode(
        image_topic=args.image_topic,
        threshold=args.threshold,
        min_area=args.min_area,
        iou_threshold=args.iou_threshold,
        max_age=args.max_age,
        class_name=args.class_name,
        frame_id=args.frame_id,
    )

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

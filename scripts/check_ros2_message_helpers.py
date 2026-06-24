#!/usr/bin/env python3

import importlib.util
from pathlib import Path

import cv2
import numpy as np


class Stamp:
    sec = 123
    nanosec = 456


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_row():
    return {
        "frame": "0",
        "image_name": "000000.png",
        "track_id": "42",
        "class_name": "car",
        "confidence": "0.75",
        "x1": "10.0",
        "y1": "20.0",
        "x2": "30.0",
        "y2": "50.0",
    }


def main():
    replay = load_module(
        "ros2/ros2_tracking_latency/ros2_tracking_latency/kitti_track_replay_node.py",
        "kitti_track_replay_node_check",
    )

    det = replay.row_to_detection(sample_row(), Stamp(), "kitti_camera")
    assert det.header.frame_id == "kitti_camera"
    assert det.id == "42"
    assert det.results[0].hypothesis.class_id == "car"
    assert det.results[0].hypothesis.score == 0.75
    assert det.bbox.center.position.x == 20.0
    assert det.bbox.center.position.y == 35.0
    assert det.bbox.size_x == 20.0
    assert det.bbox.size_y == 30.0

    row_b = sample_row()
    row_b["track_id"] = "43"
    row_b["confidence"] = "0.55"
    arr = replay.rows_to_detection_array([sample_row(), row_b], Stamp(), "kitti_camera")
    assert arr.header.frame_id == "kitti_camera"
    assert len(arr.detections) == 2
    assert [d.id for d in arr.detections] == ["42", "43"]

    diag = replay.make_diagnostic_array(
        {
            "sequence": "0001",
            "frame": 7,
            "num_tracks": 5,
            "fps": 10.0,
            "publish_latency_ms": 0.123,
        },
        Stamp(),
    )
    values = {kv.key: kv.value for kv in diag.status[0].values}
    assert diag.header.frame_id == "tracking_latency"
    assert values["sequence"] == "0001"
    assert values["frame"] == "7"
    assert values["num_tracks"] == "5"

    debug = load_module(
        "ros2/ros2_tracking_latency/ros2_tracking_latency/kitti_debug_image_replay_node.py",
        "kitti_debug_image_replay_node_check",
    )
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    out = debug.draw_tracks(image, [sample_row()], "0001", 0)
    assert out.shape == image.shape
    assert out.sum() > 0
    assert not np.array_equal(out, image)
    ok, encoded = cv2.imencode(".jpg", out)
    assert ok
    assert len(encoded) > 100

    print("ROS 2 message helper checks passed.")


if __name__ == "__main__":
    main()

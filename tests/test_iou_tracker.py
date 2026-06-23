import importlib.util
from pathlib import Path

import pandas as pd


def load_iou_tracker_module():
    path = Path("scripts/run_iou_tracker.py")
    spec = importlib.util.spec_from_file_location("run_iou_tracker", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_box_iou_matrix_identity_and_nonoverlap():
    mod = load_iou_tracker_module()
    a = [[0, 0, 10, 10], [20, 20, 30, 30]]
    b = [[0, 0, 10, 10], [100, 100, 110, 110]]
    iou = mod.box_iou_matrix(a, b)
    assert iou.shape == (2, 2)
    assert iou[0, 0] == 1.0
    assert iou[0, 1] == 0.0
    assert iou[1, 0] == 0.0


def test_simple_iou_tracker_preserves_id_for_smooth_motion():
    mod = load_iou_tracker_module()
    det = pd.DataFrame([
        {"sequence": 0, "frame": 0, "image_name": "000000.png", "class_id": 2, "class_name": "car", "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10, "latency_ms": 1.0},
        {"sequence": 0, "frame": 1, "image_name": "000001.png", "class_id": 2, "class_name": "car", "confidence": 0.8, "x1": 1, "y1": 1, "x2": 11, "y2": 11, "latency_ms": 1.0},
        {"sequence": 0, "frame": 2, "image_name": "000002.png", "class_id": 2, "class_name": "car", "confidence": 0.7, "x1": 2, "y1": 2, "x2": 12, "y2": 12, "latency_ms": 1.0},
    ])
    tracks = mod.run_iou_tracker(det, iou_threshold=0.3, max_age=2)
    assert len(tracks) == 3
    assert tracks["track_id"].nunique() == 1
    assert tracks["track_id"].tolist() == [1, 1, 1]


def test_simple_iou_tracker_creates_new_id_for_far_jump():
    mod = load_iou_tracker_module()
    det = pd.DataFrame([
        {"sequence": 0, "frame": 0, "image_name": "000000.png", "class_id": 2, "class_name": "car", "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10, "latency_ms": 1.0},
        {"sequence": 0, "frame": 1, "image_name": "000001.png", "class_id": 2, "class_name": "car", "confidence": 0.8, "x1": 100, "y1": 100, "x2": 110, "y2": 110, "latency_ms": 1.0},
    ])
    tracks = mod.run_iou_tracker(det, iou_threshold=0.3, max_age=2)
    assert len(tracks) == 2
    assert tracks["track_id"].tolist() == [1, 2]

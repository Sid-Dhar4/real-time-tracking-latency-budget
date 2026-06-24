import importlib.util
from pathlib import Path

import pandas as pd


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_trackeval_export_tracker_file_format(tmp_path):
    mod = load_module("scripts/export_trackeval_kitti.py", "export_trackeval_kitti")

    tracks = pd.DataFrame([
        {
            "sequence": "0000",
            "frame": 3,
            "image_name": "000003.png",
            "track_id": 7,
            "class_id": 2,
            "class_name": "car",
            "confidence": 0.75,
            "x1": 10.0,
            "y1": 20.0,
            "x2": 30.0,
            "y2": 50.0,
            "latency_ms": 1.0,
        }
    ])

    csv_path = tmp_path / "tracks.csv"
    out_path = tmp_path / "0000.txt"
    tracks.to_csv(csv_path, index=False)

    n = mod.export_tracker_file("0000", csv_path, out_path)

    assert n == 1
    line = out_path.read_text().strip()
    parts = line.split()

    assert int(parts[0]) == 3
    assert int(parts[1]) == 7
    assert parts[2] == "car"
    assert float(parts[6]) == 10.0
    assert float(parts[7]) == 20.0
    assert float(parts[8]) == 30.0
    assert float(parts[9]) == 50.0
    assert float(parts[-1]) == 0.75


def test_dropped_frame_export_removes_expected_frames(tmp_path):
    mod = load_module("scripts/export_trackeval_stress.py", "export_trackeval_stress")

    df = pd.DataFrame([
        {"frame": 0, "track_id": 1, "class_name": "car", "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10},
        {"frame": 1, "track_id": 1, "class_name": "car", "confidence": 0.9, "x1": 1, "y1": 0, "x2": 11, "y2": 10},
        {"frame": 2, "track_id": 1, "class_name": "car", "confidence": 0.9, "x1": 2, "y1": 0, "x2": 12, "y2": 10},
        {"frame": 3, "track_id": 1, "class_name": "car", "confidence": 0.9, "x1": 3, "y1": 0, "x2": 13, "y2": 10},
    ])

    dropped = df[df["frame"] % 2 != 0].copy()
    out_path = tmp_path / "drop_every_2.txt"

    n = mod.write_tracker_file(dropped, out_path)

    lines = out_path.read_text().strip().splitlines()
    frames = [int(line.split()[0]) for line in lines]

    assert n == 2
    assert frames == [1, 3]


def test_latency_summary_warmup_exclusion_artifact_is_consistent():
    df = pd.read_csv("results/tables/m9_latency_summary.csv")

    assert set(df["stage"]) == {"detector", "tracker"}
    assert (df["warmup_frames_excluded"] == 5).all()
    assert (df["frames_used"] == df["frames_with_latency"] - df["warmup_frames_excluded"]).all()
    assert (df["p95_ms"] >= df["p50_ms"]).all()
    assert (df["p99_ms"] >= df["p95_ms"]).all()
    assert (df["fps_from_mean"] > 0).all()

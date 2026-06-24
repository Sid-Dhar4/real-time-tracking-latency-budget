import importlib.util
from pathlib import Path

import pandas as pd


def load_risk_module():
    path = Path("scripts/compute_track_risk.py")
    spec = importlib.util.spec_from_file_location("compute_track_risk", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def toy_tracks():
    return pd.DataFrame([
        {
            "sequence": "0001",
            "frame": 0,
            "image_name": "000000.png",
            "track_id": 1,
            "class_id": 2,
            "class_name": "car",
            "confidence": 0.95,
            "x1": 100.0,
            "y1": 100.0,
            "x2": 200.0,
            "y2": 200.0,
            "latency_ms": 1.0,
        },
        {
            "sequence": "0001",
            "frame": 1,
            "image_name": "000001.png",
            "track_id": 1,
            "class_id": 2,
            "class_name": "car",
            "confidence": 0.93,
            "x1": 105.0,
            "y1": 100.0,
            "x2": 205.0,
            "y2": 200.0,
            "latency_ms": 1.0,
        },
        {
            "sequence": "0001",
            "frame": 2,
            "image_name": "000002.png",
            "track_id": 2,
            "class_id": 2,
            "class_name": "car",
            "confidence": 0.30,
            "x1": 1.0,
            "y1": 1.0,
            "x2": 12.0,
            "y2": 12.0,
            "latency_ms": 1.0,
        },
    ])


def test_risk_components_assign_higher_risk_to_low_confidence_border_track():
    mod = load_risk_module()
    df = toy_tracks()

    scored = mod.add_geometry(df)
    scored = mod.add_motion_features(scored)
    scored = mod.add_risk_components(scored, image_width=300.0, image_height=220.0)
    summary = mod.summarize_tracks(scored)

    risks = summary.set_index("track_id")["mean_risk_score"]

    assert risks.loc[2] > risks.loc[1]
    assert scored["risk_score"].between(0.0, 1.0).all()
    assert scored["border_risk"].max() == 1.0


def test_risk_summary_contains_expected_columns():
    mod = load_risk_module()
    df = toy_tracks()

    scored = mod.add_geometry(df)
    scored = mod.add_motion_features(scored)
    scored = mod.add_risk_components(scored, image_width=300.0, image_height=220.0)
    summary = mod.summarize_tracks(scored)

    required = {
        "frames",
        "mean_confidence",
        "mean_area",
        "mean_low_confidence_risk",
        "mean_small_box_risk",
        "mean_border_risk",
        "mean_motion_jump_risk",
        "mean_short_track_risk",
        "mean_risk_score",
        "max_risk_score",
        "risk_rank",
    }

    assert required.issubset(set(summary.columns))
    assert len(summary) == 2


def test_label_risk_thresholds():
    mod = load_risk_module()

    assert mod.label_risk(0.70) == "high"
    assert mod.label_risk(0.50) == "medium"
    assert mod.label_risk(0.20) == "low"

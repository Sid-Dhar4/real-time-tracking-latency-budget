from pathlib import Path

import pandas as pd


def test_m14_stress_metrics_degrade_monotonically():
    df = pd.read_csv("results/tables/m14_trackeval_stress_summary.csv")
    order = ["baseline", "drop_every_5", "drop_every_3", "drop_every_2"]
    df = df.set_index("variant").loc[order]
    assert df["HOTA"].is_monotonic_decreasing
    assert df["MOTA"].is_monotonic_decreasing
    assert df["IDF1"].is_monotonic_decreasing
    assert df.loc["baseline", "HOTA"] > df.loc["drop_every_2", "HOTA"]


def test_m15_bytetrack_has_better_identity_consistency_than_iou_tracker():
    df = pd.read_csv("results/tables/m15_tracker_comparison.csv").set_index("tracker")
    assert df.loc["bytetrack", "IDF1"] > df.loc["iou_tracker", "IDF1"]
    assert df.loc["bytetrack", "IDSW"] < df.loc["iou_tracker", "IDSW"]
    assert df.loc["bytetrack", "IDs"] < df.loc["iou_tracker", "IDs"]


def test_trackeval_summary_contains_core_metrics():
    text = Path("results/trackeval/m13_car_summary.txt").read_text()
    for metric in ["HOTA", "MOTA", "IDF1", "IDSW", "Dets", "GT_Dets"]:
        assert metric in text


def test_latency_summary_has_reasonable_cpu_tracker_p95():
    df = pd.read_csv("results/tables/m9_latency_summary.csv")
    tracker = df[df["stage"] == "tracker"]
    assert len(tracker) >= 2
    assert tracker["p95_ms"].max() < 30.0


def test_required_visual_artifacts_are_nonempty():
    required = [
        "results/videos/m11_seq0001_demo_overlay.mp4",
        "results/plots/m12_latency_histogram.png",
        "results/plots/m14_trackeval_stress_metrics.png",
        "results/plots/m15_tracker_comparison_metrics.png",
    ]
    for path in required:
        p = Path(path)
        assert p.is_file()
        assert p.stat().st_size > 1000

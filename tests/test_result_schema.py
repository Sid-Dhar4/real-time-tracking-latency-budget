from pathlib import Path
import pandas as pd


def require_columns(path, columns):
    assert Path(path).exists(), f"Missing file: {path}"
    df = pd.read_csv(path)
    missing = [c for c in columns if c not in df.columns]
    assert not missing, f"{path} missing columns: {missing}"
    assert len(df) > 0, f"{path} is empty"
    return df


def test_metrics_csv_schema():
    df = require_columns(
        "results/metrics.csv",
        [
            "sequence", "class_name", "iou_threshold", "total_gt", "total_pred",
            "tp", "fp", "fn", "id_switches", "precision", "recall",
            "mota_like", "idf1_like", "evaluator",
        ],
    )
    assert df["precision"].between(0, 1).all()
    assert df["recall"].between(0, 1).all()
    assert df["idf1_like"].between(0, 1).all()


def test_sweep_results_schema():
    df = require_columns(
        "results/sweep_results.csv",
        [
            "sequence", "confidence_threshold", "class_name", "precision", "recall",
            "mota_like", "idf1_like", "fp", "fn", "id_switches",
            "mean_latency_ms", "p95_latency_ms", "fps_estimate",
        ],
    )
    assert df["confidence_threshold"].is_monotonic_increasing
    assert df["precision"].between(0, 1).all()
    assert df["recall"].between(0, 1).all()
    assert df["mean_latency_ms"].gt(0).all()
    assert df["p95_latency_ms"].gt(0).all()


def test_multiseq_summary_schema():
    df = require_columns(
        "results/tables/m8_multiseq_summary.csv",
        [
            "sequence", "class_name", "total_gt", "total_pred", "tp", "fp",
            "fn", "id_switches", "precision", "recall", "mota_like", "idf1_like",
        ],
    )
    assert set(df["sequence"].astype(str)) == {"0000", "0001"}
    assert df["total_gt"].gt(0).all()


def test_latency_summary_schema():
    df = require_columns(
        "results/tables/m9_latency_summary.csv",
        [
            "sequence", "stage", "frames_with_latency", "warmup_frames_excluded",
            "frames_used", "mean_ms", "p50_ms", "p90_ms", "p95_ms", "p99_ms",
            "max_ms", "fps_from_mean", "device",
        ],
    )
    assert set(df["stage"]) == {"detector", "tracker"}
    assert set(df["sequence"].astype(str)) == {"0000", "0001"}
    assert df["frames_used"].gt(0).all()
    assert df["mean_ms"].gt(0).all()
    assert df["p95_ms"].ge(df["p50_ms"]).all()

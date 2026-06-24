#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def normalize_01(series):
    series = series.astype(float)
    lo = float(series.min())
    hi = float(series.max())
    if hi <= lo:
        return series * 0.0
    return (series - lo) / (hi - lo)


def add_geometry(df):
    df = df.copy()
    df["width"] = (df["x2"] - df["x1"]).clip(lower=0.0)
    df["height"] = (df["y2"] - df["y1"]).clip(lower=0.0)
    df["area"] = df["width"] * df["height"]
    df["cx"] = (df["x1"] + df["x2"]) / 2.0
    df["cy"] = (df["y1"] + df["y2"]) / 2.0
    return df


def add_motion_features(df):
    df = df.sort_values(["track_id", "frame"]).copy()
    df["prev_cx"] = df.groupby("track_id")["cx"].shift(1)
    df["prev_cy"] = df.groupby("track_id")["cy"].shift(1)
    df["prev_frame"] = df.groupby("track_id")["frame"].shift(1)

    dx = df["cx"] - df["prev_cx"]
    dy = df["cy"] - df["prev_cy"]
    gap = (df["frame"] - df["prev_frame"]).fillna(1).clip(lower=1)

    df["center_jump_px"] = ((dx * dx + dy * dy) ** 0.5).fillna(0.0)
    df["center_jump_per_frame_px"] = df["center_jump_px"] / gap
    df["frame_gap"] = gap
    return df


def add_risk_components(df, image_width=1242.0, image_height=375.0):
    df = df.copy()

    df["low_confidence_risk"] = (1.0 - df["confidence"].astype(float)).clip(0.0, 1.0)

    area_norm = normalize_01(df["area"])
    df["small_box_risk"] = (1.0 - area_norm).clip(0.0, 1.0)

    margin = 20.0
    near_left = df["x1"] <= margin
    near_top = df["y1"] <= margin
    near_right = df["x2"] >= image_width - margin
    near_bottom = df["y2"] >= image_height - margin
    df["border_risk"] = (near_left | near_top | near_right | near_bottom).astype(float)

    jump_norm = normalize_01(df["center_jump_per_frame_px"])
    df["motion_jump_risk"] = jump_norm.clip(0.0, 1.0)

    track_len = df.groupby("track_id")["frame"].transform("nunique")
    df["track_length"] = track_len
    df["short_track_risk"] = (1.0 / track_len.clip(lower=1)).clip(0.0, 1.0)

    weights = {
        "low_confidence_risk": 0.25,
        "small_box_risk": 0.20,
        "border_risk": 0.15,
        "motion_jump_risk": 0.25,
        "short_track_risk": 0.15,
    }

    df["risk_score"] = 0.0
    for name, weight in weights.items():
        df["risk_score"] += weight * df[name]

    df["risk_score"] = df["risk_score"].clip(0.0, 1.0)
    return df


def label_risk(score):
    if score >= 0.65:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def summarize_tracks(df):
    summary = df.groupby(["sequence", "track_id", "class_name"]).agg(
        frames=("frame", "nunique"),
        first_frame=("frame", "min"),
        last_frame=("frame", "max"),
        mean_confidence=("confidence", "mean"),
        min_confidence=("confidence", "min"),
        mean_area=("area", "mean"),
        max_center_jump_per_frame_px=("center_jump_per_frame_px", "max"),
        mean_low_confidence_risk=("low_confidence_risk", "mean"),
        mean_small_box_risk=("small_box_risk", "mean"),
        mean_border_risk=("border_risk", "mean"),
        mean_motion_jump_risk=("motion_jump_risk", "mean"),
        mean_short_track_risk=("short_track_risk", "mean"),
        mean_risk_score=("risk_score", "mean"),
        max_risk_score=("risk_score", "max"),
    ).reset_index()

    summary["risk_rank"] = summary["mean_risk_score"].rank(method="first", ascending=False).astype(int)
    summary = summary.sort_values(["mean_risk_score", "max_risk_score"], ascending=False)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracks-csv", default="results/tracks/yolov8n_bytetrack_seq0001_tracks.csv")
    parser.add_argument("--frame-output", default="results/tables/m33_frame_risk_scores.csv")
    parser.add_argument("--track-output", default="results/tables/m33_track_risk_summary.csv")
    parser.add_argument("--top-k-output", default="results/tables/m33_top_risky_tracks.csv")
    parser.add_argument("--image-width", type=float, default=1242.0)
    parser.add_argument("--image-height", type=float, default=375.0)
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    df = pd.read_csv(args.tracks_csv)
    df = add_geometry(df)
    df = add_motion_features(df)
    df = add_risk_components(df, args.image_width, args.image_height)

    summary = summarize_tracks(df)
    summary["risk_level"] = summary["mean_risk_score"].map(label_risk)
    top = summary.head(args.top_k).copy()

    Path(args.frame_output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.frame_output, index=False)
    summary.to_csv(args.track_output, index=False)
    top.to_csv(args.top_k_output, index=False)

    print("wrote", args.frame_output, "rows", len(df))
    print("wrote", args.track_output, "rows", len(summary))
    print("wrote", args.top_k_output, "rows", len(top))
    print(top[["track_id", "frames", "mean_confidence", "mean_risk_score", "risk_level"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RISK_ORDER = ["low", "medium", "high"]


def iou_xyxy(a, b) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter

    return inter / union if union > 0 else 0.0


def load_kitti_gt(label_path: Path, class_name: str) -> pd.DataFrame:
    rows = []
    wanted = class_name.lower()

    with label_path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 10:
                continue

            frame = int(parts[0])
            object_id = int(parts[1])
            cls = parts[2]

            if cls.lower() != wanted:
                continue
            if object_id < 0:
                continue

            rows.append(
                {
                    "frame": frame,
                    "gt_id": object_id,
                    "class_name": cls,
                    "x1": float(parts[6]),
                    "y1": float(parts[7]),
                    "x2": float(parts[8]),
                    "y2": float(parts[9]),
                }
            )

    return pd.DataFrame(rows)


def greedy_match_frame(gt: pd.DataFrame, pred: pd.DataFrame, iou_threshold: float) -> tuple[list[dict], set[int], set[int]]:
    candidates = []

    for gi, grow in gt.iterrows():
        gbox = (grow.x1, grow.y1, grow.x2, grow.y2)
        for pi, prow in pred.iterrows():
            pbox = (prow.x1, prow.y1, prow.x2, prow.y2)
            iou = iou_xyxy(gbox, pbox)
            if iou >= iou_threshold:
                candidates.append((iou, gi, pi))

    candidates.sort(reverse=True, key=lambda x: x[0])

    matched_gt = set()
    matched_pred = set()
    matches = []

    for iou, gi, pi in candidates:
        if gi in matched_gt or pi in matched_pred:
            continue

        matched_gt.add(gi)
        matched_pred.add(pi)

        grow = gt.loc[gi]
        prow = pred.loc[pi]

        matches.append(
            {
                "frame": int(grow.frame),
                "gt_id": int(grow.gt_id),
                "track_id": int(prow.track_id),
                "iou": float(iou),
                "risk_score": float(prow.risk_score),
                "risk_level": str(prow.risk_level),
                "confidence": float(prow.confidence),
            }
        )

    return matches, matched_gt, matched_pred


def build_diagnostics(gt: pd.DataFrame, pred: pd.DataFrame, iou_threshold: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_matches = []
    pred_rows = []
    frame_rows = []

    prev_gt_to_track = {}
    id_switch_events = []

    all_frames = sorted(set(gt["frame"].unique()).union(set(pred["frame"].unique())))

    for frame in all_frames:
        gt_f = gt[gt["frame"] == frame].copy()
        pred_f = pred[pred["frame"] == frame].copy()

        matches, matched_gt_idx, matched_pred_idx = greedy_match_frame(gt_f, pred_f, iou_threshold)

        frame_idsw = 0
        for m in matches:
            gt_id = m["gt_id"]
            track_id = m["track_id"]
            previous = prev_gt_to_track.get(gt_id)

            if previous is not None and previous != track_id:
                m["id_switch_event"] = 1
                m["previous_track_id"] = previous
                frame_idsw += 1
                id_switch_events.append(m.copy())
            else:
                m["id_switch_event"] = 0
                m["previous_track_id"] = -1

            prev_gt_to_track[gt_id] = track_id
            all_matches.append(m)

        matched_pred_track_rows = set(pred_f.loc[list(matched_pred_idx)].index) if matched_pred_idx else set()

        for pi, prow in pred_f.iterrows():
            pred_rows.append(
                {
                    "frame": int(frame),
                    "track_id": int(prow.track_id),
                    "risk_score": float(prow.risk_score),
                    "risk_level": str(prow.risk_level),
                    "confidence": float(prow.confidence),
                    "matched_to_gt": int(pi in matched_pred_track_rows),
                }
            )

        fp = len(pred_f) - len(matched_pred_idx)
        fn = len(gt_f) - len(matched_gt_idx)

        if len(pred_f) > 0:
            mean_risk = float(pred_f["risk_score"].mean())
            max_risk = float(pred_f["risk_score"].max())
            high_or_medium = int((pred_f["risk_level"].isin(["medium", "high"])).sum())
        else:
            mean_risk = 0.0
            max_risk = 0.0
            high_or_medium = 0

        frame_rows.append(
            {
                "frame": int(frame),
                "gt_count": int(len(gt_f)),
                "pred_count": int(len(pred_f)),
                "tp": int(len(matches)),
                "fp": int(fp),
                "fn": int(fn),
                "id_switches": int(frame_idsw),
                "mean_risk_score": mean_risk,
                "max_risk_score": max_risk,
                "medium_or_high_risk_detections": high_or_medium,
            }
        )

    return pd.DataFrame(all_matches), pd.DataFrame(pred_rows), pd.DataFrame(frame_rows)


def summarize_id_switches(track_diag: pd.DataFrame) -> pd.DataFrame:
    out = (
        track_diag.groupby("risk_level", observed=False)
        .agg(
            track_count=("track_id", "count"),
            mean_risk_score=("mean_risk_score", "mean"),
            mean_frames=("frames", "mean"),
            tracks_with_id_switch=("has_id_switch", "sum"),
            total_id_switch_events=("id_switch_events", "sum"),
        )
        .reset_index()
    )

    out["id_switch_track_rate"] = out["tracks_with_id_switch"] / out["track_count"].clip(lower=1)
    return out


def summarize_fragmentation(track_diag: pd.DataFrame) -> pd.DataFrame:
    out = (
        track_diag.groupby("risk_level", observed=False)
        .agg(
            track_count=("track_id", "count"),
            mean_risk_score=("mean_risk_score", "mean"),
            mean_frames=("frames", "mean"),
            median_frames=("frames", "median"),
            short_tracks=("is_short_track", "sum"),
            fragmented_tracks=("is_fragmented", "sum"),
            mean_gap_count=("gap_count", "mean"),
        )
        .reset_index()
    )

    out["short_track_rate"] = out["short_tracks"] / out["track_count"].clip(lower=1)
    out["fragmented_track_rate"] = out["fragmented_tracks"] / out["track_count"].clip(lower=1)
    return out


def summarize_frame_failures(frame_diag: pd.DataFrame) -> pd.DataFrame:
    df = frame_diag.copy()

    # Robust tertile buckets even when risk values repeat.
    df["frame_risk_bucket"] = pd.qcut(
        df["max_risk_score"].rank(method="first"),
        q=3,
        labels=RISK_ORDER,
    )

    out = (
        df.groupby("frame_risk_bucket", observed=False)
        .agg(
            frame_count=("frame", "count"),
            mean_max_risk_score=("max_risk_score", "mean"),
            mean_risk_score=("mean_risk_score", "mean"),
            total_fn=("fn", "sum"),
            total_fp=("fp", "sum"),
            total_id_switches=("id_switches", "sum"),
            mean_fn_per_frame=("fn", "mean"),
            mean_fp_per_frame=("fp", "mean"),
            frames_with_fn=("fn", lambda s: int((s > 0).sum())),
            frames_with_fp=("fp", lambda s: int((s > 0).sum())),
        )
        .reset_index()
        .rename(columns={"frame_risk_bucket": "risk_bucket"})
    )

    out["fn_frame_rate"] = out["frames_with_fn"] / out["frame_count"].clip(lower=1)
    out["fp_frame_rate"] = out["frames_with_fp"] / out["frame_count"].clip(lower=1)
    return out


def make_plot(idsw: pd.DataFrame, frag: pd.DataFrame, frame_fail: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    plot_rows = []

    for _, row in frag.iterrows():
        plot_rows.append(
            {
                "bucket": row["risk_level"],
                "metric": "short_track_rate",
                "value": row["short_track_rate"],
            }
        )

    for _, row in idsw.iterrows():
        plot_rows.append(
            {
                "bucket": row["risk_level"],
                "metric": "id_switch_track_rate",
                "value": row["id_switch_track_rate"],
            }
        )

    for _, row in frame_fail.iterrows():
        plot_rows.append(
            {
                "bucket": row["risk_bucket"],
                "metric": "fn_frame_rate",
                "value": row["fn_frame_rate"],
            }
        )

    plot_df = pd.DataFrame(plot_rows)
    pivot = plot_df.pivot(index="bucket", columns="metric", values="value").reindex(RISK_ORDER)

    ax = pivot.plot(kind="bar", figsize=(8, 5))
    ax.set_title("Risk buckets vs local failure diagnostics")
    ax.set_xlabel("risk bucket")
    ax.set_ylabel("rate")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def write_report(idsw: pd.DataFrame, frag: pd.DataFrame, frame_fail: pd.DataFrame, output: Path) -> None:
    def fmt_table(df: pd.DataFrame) -> str:
        return df.round(4).to_markdown(index=False)

    report = f"""# Risk vs Failure Correlation

This report compares deterministic track-risk scores against local tracking failure diagnostics.

## Purpose

The previous risk validation showed that higher-risk tracks were shorter-lived and lower-confidence. This report goes further by comparing risk buckets against local failure signals:

- ID-switch-associated tracks
- false-positive-like unmatched detections
- false-negative frame burden
- track fragmentation and short-track rates

## Claim boundary

This is a local diagnostic analysis, not an official KITTI leaderboard result and not an official TrackEval failure attribution. Matching is performed with local greedy IoU association against KITTI training labels for sequence `0001`.

The goal is to test whether the risk score is directionally useful for debugging and downstream robot-facing diagnostics.

## Risk vs ID switches

{fmt_table(idsw)}

## Risk vs track fragmentation

{fmt_table(frag)}

## Frame risk burden vs false negatives / false positives

{fmt_table(frame_fail)}

## Interpretation

A risk monitor is most useful when higher-risk buckets show worse stability or failure burden than lower-risk buckets. The tables above quantify that relationship for sequence `0001`.

The strongest expected relationship is between risk and track fragmentation / short track duration, because the risk score directly includes short-track and motion-stability components.

ID-switch and false-negative correlations are more indirect. They should be interpreted as diagnostic signals, not causal proof.

## Outputs

- `results/tables/m43_risk_vs_id_switches.csv`
- `results/tables/m43_risk_vs_false_negatives.csv`
- `results/tables/m43_risk_vs_track_fragmentation.csv`
- `results/tables/m43_track_failure_diagnostics.csv`
- `results/tables/m43_frame_failure_diagnostics.csv`
- `results/plots/m43_risk_vs_failure_rate.png`
"""

    output.write_text(report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--risk-summary", type=Path, default=Path("results/tables/m33_track_risk_summary.csv"))
    parser.add_argument("--frame-risk", type=Path, default=Path("results/tables/m33_frame_risk_scores.csv"))
    parser.add_argument("--gt-labels", type=Path, default=Path("data/kitti_tracking/training/label_02/0001.txt"))
    parser.add_argument("--class-name", default="Car")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    args = parser.parse_args()

    out_tables = Path("results/tables")
    out_plots = Path("results/plots")
    out_reports = Path("reports")
    out_tables.mkdir(parents=True, exist_ok=True)
    out_plots.mkdir(parents=True, exist_ok=True)
    out_reports.mkdir(parents=True, exist_ok=True)

    risk_summary = pd.read_csv(args.risk_summary)
    frame_risk = pd.read_csv(args.frame_risk)

    risk_summary["risk_level"] = pd.Categorical(risk_summary["risk_level"], categories=RISK_ORDER, ordered=True)

    class_lower = args.class_name.lower()
    risk_summary = risk_summary[risk_summary["class_name"].str.lower() == class_lower].copy()
    pred = frame_risk[frame_risk["class_name"].str.lower() == class_lower].copy()
    pred["risk_level"] = pd.Categorical(pred["risk_score"].map(lambda x: "high" if x >= 0.65 else ("medium" if x >= 0.45 else "low")), categories=RISK_ORDER, ordered=True)

    gt = load_kitti_gt(args.gt_labels, args.class_name)

    matches, pred_diag, frame_diag = build_diagnostics(gt, pred, args.iou_threshold)

    idsw_by_track = (
        matches.groupby("track_id")["id_switch_event"].sum().rename("id_switch_events")
        if not matches.empty
        else pd.Series(dtype=float, name="id_switch_events")
    )

    pred_unmatched = pred_diag.copy()
    pred_unmatched["unmatched_detection"] = 1 - pred_unmatched["matched_to_gt"]
    fp_by_track = pred_unmatched.groupby("track_id").agg(
        pred_detections=("matched_to_gt", "count"),
        unmatched_detections=("unmatched_detection", "sum"),
    )

    track_frames = pred.groupby("track_id").agg(
        observed_frames=("frame", "nunique"),
        first_observed_frame=("frame", "min"),
        last_observed_frame=("frame", "max"),
    )
    track_frames["span_frames"] = track_frames["last_observed_frame"] - track_frames["first_observed_frame"] + 1
    track_frames["gap_count"] = track_frames["span_frames"] - track_frames["observed_frames"]

    track_diag = risk_summary.merge(idsw_by_track, on="track_id", how="left")
    track_diag = track_diag.merge(fp_by_track, on="track_id", how="left")
    track_diag = track_diag.merge(track_frames[["gap_count"]], on="track_id", how="left")

    track_diag["id_switch_events"] = track_diag["id_switch_events"].fillna(0).astype(int)
    track_diag["pred_detections"] = track_diag["pred_detections"].fillna(0).astype(int)
    track_diag["unmatched_detections"] = track_diag["unmatched_detections"].fillna(0).astype(int)
    track_diag["gap_count"] = track_diag["gap_count"].fillna(0).astype(int)

    track_diag["has_id_switch"] = track_diag["id_switch_events"] > 0
    track_diag["is_short_track"] = track_diag["frames"] <= 3
    track_diag["is_fragmented"] = track_diag["is_short_track"] | (track_diag["gap_count"] > 0)
    track_diag["unmatched_detection_rate"] = track_diag["unmatched_detections"] / track_diag["pred_detections"].clip(lower=1)

    idsw = summarize_id_switches(track_diag)
    frag = summarize_fragmentation(track_diag)
    frame_fail = summarize_frame_failures(frame_diag)

    idsw.to_csv(out_tables / "m43_risk_vs_id_switches.csv", index=False)
    frame_fail.to_csv(out_tables / "m43_risk_vs_false_negatives.csv", index=False)
    frag.to_csv(out_tables / "m43_risk_vs_track_fragmentation.csv", index=False)
    track_diag.to_csv(out_tables / "m43_track_failure_diagnostics.csv", index=False)
    frame_diag.to_csv(out_tables / "m43_frame_failure_diagnostics.csv", index=False)

    make_plot(idsw, frag, frame_fail, out_plots / "m43_risk_vs_failure_rate.png")
    write_report(idsw, frag, frame_fail, out_reports / "risk_failure_correlation.md")

    print("wrote m43 risk/failure outputs")
    print()
    print("risk vs id switches")
    print(idsw.round(4).to_string(index=False))
    print()
    print("risk vs fragmentation")
    print(frag.round(4).to_string(index=False))
    print()
    print("frame risk vs false negatives")
    print(frame_fail.round(4).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

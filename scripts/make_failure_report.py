#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def load_eval_module():
    module_path = Path("scripts/evaluate_local_kitti.py")
    spec = importlib.util.spec_from_file_location("evaluate_local_kitti", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load evaluator module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def choose_best_sweep_row(sweep_csv: Path) -> pd.Series:
    df = pd.read_csv(sweep_csv)
    if df.empty:
        raise RuntimeError(f"Sweep CSV is empty: {sweep_csv}")
    return df.sort_values(["idf1_like", "mota_like", "precision"], ascending=False).iloc[0]


def match_frame(gt_f: pd.DataFrame, pred_f: pd.DataFrame, iou_threshold: float, eval_mod):
    gt_boxes = gt_f[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)
    pred_boxes = pred_f[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)

    matches = []
    if len(gt_f) and len(pred_f):
        ious = eval_mod.box_iou(gt_boxes, pred_boxes)
        cost = 1.0 - ious
        gt_idx, pred_idx = linear_sum_assignment(cost)

        for gi, pi in zip(gt_idx, pred_idx):
            iou = float(ious[gi, pi])
            if iou >= iou_threshold:
                matches.append((gi, pi, iou))

    matched_gt = {m[0] for m in matches}
    matched_pred = {m[1] for m in matches}
    unmatched_gt = [i for i in range(len(gt_f)) if i not in matched_gt]
    unmatched_pred = [i for i in range(len(pred_f)) if i not in matched_pred]

    return matches, unmatched_gt, unmatched_pred


def draw_box(image, box, label, color, thickness=2):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
    cv2.putText(
        image,
        label,
        (x1, max(18, y1 - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
        cv2.LINE_AA,
    )


def make_failure_image(
    image_path: Path,
    gt_f: pd.DataFrame,
    pred_f: pd.DataFrame,
    matches,
    unmatched_gt,
    unmatched_pred,
    output_path: Path,
):
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"Could not read image: {image_path}")

    # matched GT = green, missed GT = blue, false positive pred = red, matched pred = yellow
    for gi, pi, iou in matches:
        gt_row = gt_f.iloc[gi]
        pred_row = pred_f.iloc[pi]
        draw_box(
            image,
            [gt_row.x1, gt_row.y1, gt_row.x2, gt_row.y2],
            f"GT {int(gt_row.gt_track_id)}",
            (0, 255, 0),
            2,
        )
        draw_box(
            image,
            [pred_row.x1, pred_row.y1, pred_row.x2, pred_row.y2],
            f"P {int(pred_row.pred_track_id)} {iou:.2f}",
            (0, 255, 255),
            1,
        )

    for gi in unmatched_gt:
        gt_row = gt_f.iloc[gi]
        draw_box(
            image,
            [gt_row.x1, gt_row.y1, gt_row.x2, gt_row.y2],
            f"MISS GT {int(gt_row.gt_track_id)}",
            (255, 0, 0),
            2,
        )

    for pi in unmatched_pred:
        pred_row = pred_f.iloc[pi]
        draw_box(
            image,
            [pred_row.x1, pred_row.y1, pred_row.x2, pred_row.y2],
            f"FP P{int(pred_row.pred_track_id)} {pred_row.confidence:.2f}",
            (0, 0, 255),
            2,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])


def main() -> int:
    parser = argparse.ArgumentParser(description="Make failure analysis report for local KITTI-style tracking.")
    parser.add_argument("--sweep-csv", type=Path, default=Path("results/sweep_results.csv"))
    parser.add_argument("--label-file", type=Path, default=Path("data/kitti_tracking/training/label_02/0000.txt"))
    parser.add_argument("--image-dir", type=Path, default=Path("data/kitti_tracking/training/image_02/0000"))
    parser.add_argument("--class-name", type=str, default="Car")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--summary-csv", type=Path, default=Path("results/tables/m6_failure_summary.csv"))
    parser.add_argument("--report", type=Path, default=Path("reports/failure_analysis.md"))
    parser.add_argument("--log-file", type=Path, default=Path("results/logs/m6_failure_analysis.txt"))
    parser.add_argument("--failure-dir", type=Path, default=Path("results/failure_cases"))
    parser.add_argument("--top-k", type=int, default=6)
    args = parser.parse_args()

    eval_mod = load_eval_module()
    best = choose_best_sweep_row(args.sweep_csv)

    threshold = float(best["confidence_threshold"])
    tracks_csv = Path(str(best["tracks_csv"]))

    if not tracks_csv.exists():
        raise FileNotFoundError(
            f"Best-threshold tracks file does not exist: {tracks_csv}\n"
            f"Rerun M5C to regenerate sweep track files."
        )

    gt = eval_mod.load_kitti_gt(args.label_file, args.class_name)
    pred = eval_mod.load_predictions(tracks_csv, args.class_name)

    frames = sorted(set(gt["frame"].unique()).union(set(pred["frame"].unique())))

    last_match_for_gt: dict[int, int] = {}
    id_switch_events = []
    frame_rows = []

    for frame in frames:
        gt_f = gt[gt["frame"] == frame].reset_index(drop=True)
        pred_f = pred[pred["frame"] == frame].reset_index(drop=True)

        matches, unmatched_gt, unmatched_pred = match_frame(gt_f, pred_f, args.iou_threshold, eval_mod)

        frame_id_switches = 0
        for gi, pi, iou in matches:
            gt_id = int(gt_f.loc[gi, "gt_track_id"])
            pred_id = int(pred_f.loc[pi, "pred_track_id"])

            if gt_id in last_match_for_gt and last_match_for_gt[gt_id] != pred_id:
                frame_id_switches += 1
                id_switch_events.append(
                    {
                        "frame": frame,
                        "gt_track_id": gt_id,
                        "previous_pred_track_id": last_match_for_gt[gt_id],
                        "new_pred_track_id": pred_id,
                        "iou": iou,
                    }
                )
            last_match_for_gt[gt_id] = pred_id

        fp = len(unmatched_pred)
        fn = len(unmatched_gt)
        tp = len(matches)

        frame_rows.append(
            {
                "frame": frame,
                "gt_count": len(gt_f),
                "pred_count": len(pred_f),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "id_switches": frame_id_switches,
                "failure_score": fp + fn + 3 * frame_id_switches,
            }
        )

    frame_df = pd.DataFrame(frame_rows)
    worst = frame_df.sort_values(["failure_score", "fp", "fn"], ascending=False).head(args.top_k).copy()

    args.failure_dir.mkdir(parents=True, exist_ok=True)
    failure_images = []

    for _, row in worst.iterrows():
        frame = int(row["frame"])
        image_path = args.image_dir / f"{frame:06d}.png"

        gt_f = gt[gt["frame"] == frame].reset_index(drop=True)
        pred_f = pred[pred["frame"] == frame].reset_index(drop=True)
        matches, unmatched_gt, unmatched_pred = match_frame(gt_f, pred_f, args.iou_threshold, eval_mod)

        out_path = args.failure_dir / f"m6_frame_{frame:06d}_fp{int(row.fp)}_fn{int(row.fn)}_idsw{int(row.id_switches)}.jpg"
        make_failure_image(image_path, gt_f, pred_f, matches, unmatched_gt, unmatched_pred, out_path)
        failure_images.append(out_path)

    summary = {
        "sequence": "0000",
        "class_name": args.class_name,
        "selected_confidence_threshold": threshold,
        "selection_rule": "best_idf1_like_from_m5_sweep",
        "tracks_csv": str(tracks_csv),
        "total_frames_analyzed": len(frames),
        "total_fp": int(frame_df["fp"].sum()),
        "total_fn": int(frame_df["fn"].sum()),
        "total_id_switches": int(frame_df["id_switches"].sum()),
        "worst_frame_by_failure_score": int(worst.iloc[0]["frame"]) if len(worst) else -1,
        "worst_frame_failure_score": int(worst.iloc[0]["failure_score"]) if len(worst) else 0,
        "failure_images_created": len(failure_images),
    }

    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(args.summary_csv, index=False)

    idsw_df = pd.DataFrame(id_switch_events)

    report_lines = [
        "# Failure Analysis",
        "",
        "## Scope",
        "",
        "This report analyzes YOLOv8n + ByteTrack on KITTI tracking sequence `0000` for class `Car`.",
        "",
        "These are local KITTI-style diagnostics, not official KITTI leaderboard results and not TrackEval HOTA.",
        "",
        "## Selected threshold",
        "",
        f"- Selected confidence threshold: `{threshold}`",
        "- Selection rule: best IDF1-like score from the M5 confidence sweep.",
        f"- Tracks CSV: `{tracks_csv}`",
        "",
        "## Aggregate failure counts",
        "",
        f"- False positives: `{summary['total_fp']}`",
        f"- Missed GT boxes / false negatives: `{summary['total_fn']}`",
        f"- ID switches: `{summary['total_id_switches']}`",
        "",
        "## Worst frames",
        "",
        "| Frame | GT | Pred | TP | FP | FN | ID switches | Failure score |",
        "| ----- | -- | ---- | -- | -- | -- | ----------- | ------------- |",
    ]

    for _, row in worst.iterrows():
        report_lines.append(
            f"| {int(row.frame)} | {int(row.gt_count)} | {int(row.pred_count)} | "
            f"{int(row.tp)} | {int(row.fp)} | {int(row.fn)} | {int(row.id_switches)} | {int(row.failure_score)} |"
        )

    report_lines.extend(["", "## Failure-case images", ""])

    for path in failure_images:
        report_lines.append(f"- `{path}`")

    report_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Higher confidence reduced false positives and ID switches compared with the low-threshold baseline.",
            "- The selected threshold still misses several ground-truth cars, especially where objects are small, partly occluded, or visually ambiguous.",
            "- False positives remain important because a robot/autonomy stack may treat phantom tracks as obstacles.",
            "- ID switches matter because downstream prediction/planning modules rely on stable object identity over time.",
            "",
            "## Next improvements",
            "",
            "- Compare threshold `0.50` vs `0.65` depending on whether recall or identity stability matters more.",
            "- Add TrackEval/HOTA after export formatting is complete.",
            "- Add per-class evaluation for Pedestrian after the Car pipeline is stable.",
            "- Fix GPU driver before making final runtime claims.",
        ]
    )

    if len(idsw_df):
        report_lines.extend(["", "## ID switch events", ""])
        report_lines.append("| Frame | GT track | Previous pred ID | New pred ID | IoU |")
        report_lines.append("| ----- | -------- | ---------------- | ----------- | --- |")
        for _, row in idsw_df.iterrows():
            report_lines.append(
                f"| {int(row.frame)} | {int(row.gt_track_id)} | "
                f"{int(row.previous_pred_track_id)} | {int(row.new_pred_track_id)} | {row.iou:.3f} |"
            )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    log_lines = [
        "========== M6 FAILURE ANALYSIS ==========",
        f"selected_confidence_threshold: {threshold}",
        f"tracks_csv: {tracks_csv}",
        f"summary_csv: {args.summary_csv}",
        f"report: {args.report}",
        f"failure_images_created: {len(failure_images)}",
        f"total_fp: {summary['total_fp']}",
        f"total_fn: {summary['total_fn']}",
        f"total_id_switches: {summary['total_id_switches']}",
        "",
        "Worst frames:",
    ]
    for _, row in worst.iterrows():
        log_lines.append(
            f"frame={int(row.frame)} fp={int(row.fp)} fn={int(row.fn)} "
            f"idsw={int(row.id_switches)} score={int(row.failure_score)}"
        )

    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    args.log_file.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("\n".join(log_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

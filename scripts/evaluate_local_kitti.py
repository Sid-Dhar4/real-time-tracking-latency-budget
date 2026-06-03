#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def box_iou(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)), dtype=float)

    ax1, ay1, ax2, ay2 = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
    bx1, by1, bx2, by2 = b[:, 0], b[:, 1], b[:, 2], b[:, 3]

    ix1 = np.maximum(ax1[:, None], bx1[None, :])
    iy1 = np.maximum(ay1[:, None], by1[None, :])
    ix2 = np.minimum(ax2[:, None], bx2[None, :])
    iy2 = np.minimum(ay2[:, None], by2[None, :])

    iw = np.maximum(0.0, ix2 - ix1)
    ih = np.maximum(0.0, iy2 - iy1)
    inter = iw * ih

    area_a = np.maximum(0.0, ax2 - ax1) * np.maximum(0.0, ay2 - ay1)
    area_b = np.maximum(0.0, bx2 - bx1) * np.maximum(0.0, by2 - by1)

    union = area_a[:, None] + area_b[None, :] - inter
    return np.where(union > 0, inter / union, 0.0)


def load_kitti_gt(label_file: Path, class_name: str) -> pd.DataFrame:
    rows = []

    with label_file.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            # KITTI tracking label format:
            # frame track_id type truncated occluded alpha bbox_left bbox_top bbox_right bbox_bottom ...
            frame = int(parts[0])
            track_id = int(parts[1])
            obj_type = parts[2]

            if obj_type != class_name:
                continue

            x1 = float(parts[6])
            y1 = float(parts[7])
            x2 = float(parts[8])
            y2 = float(parts[9])

            rows.append(
                {
                    "frame": frame,
                    "gt_track_id": track_id,
                    "class_name": obj_type,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                }
            )

    return pd.DataFrame(rows)


def load_predictions(tracks_csv: Path, class_name: str) -> pd.DataFrame:
    df = pd.read_csv(tracks_csv)
    df = df[df["class_name"].str.lower() == class_name.lower()].copy()
    df = df.rename(columns={"track_id": "pred_track_id"})
    return df


def evaluate(gt: pd.DataFrame, pred: pd.DataFrame, iou_threshold: float) -> dict:
    frames = sorted(set(gt["frame"].unique()).union(set(pred["frame"].unique())))

    total_gt = len(gt)
    total_pred = len(pred)
    tp = 0
    fp = 0
    fn = 0
    id_switches = 0

    # For a simple CLEAR-MOT-style ID switch count.
    last_match_for_gt: dict[int, int] = {}

    # For a simple IDF1-style global identity matching.
    pair_counts: dict[tuple[int, int], int] = defaultdict(int)

    per_frame_rows = []

    for frame in frames:
        gt_f = gt[gt["frame"] == frame].reset_index(drop=True)
        pred_f = pred[pred["frame"] == frame].reset_index(drop=True)

        gt_boxes = gt_f[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)
        pred_boxes = pred_f[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)

        matches = []

        if len(gt_f) > 0 and len(pred_f) > 0:
            ious = box_iou(gt_boxes, pred_boxes)
            cost = 1.0 - ious
            gt_idx, pred_idx = linear_sum_assignment(cost)

            for gi, pi in zip(gt_idx, pred_idx):
                iou = ious[gi, pi]
                if iou >= iou_threshold:
                    gt_id = int(gt_f.loc[gi, "gt_track_id"])
                    pred_id = int(pred_f.loc[pi, "pred_track_id"])
                    matches.append((gi, pi, gt_id, pred_id, float(iou)))

        matched_gt = {m[0] for m in matches}
        matched_pred = {m[1] for m in matches}

        frame_tp = len(matches)
        frame_fn = len(gt_f) - len(matched_gt)
        frame_fp = len(pred_f) - len(matched_pred)

        tp += frame_tp
        fn += frame_fn
        fp += frame_fp

        for _, _, gt_id, pred_id, _ in matches:
            pair_counts[(gt_id, pred_id)] += 1
            if gt_id in last_match_for_gt and last_match_for_gt[gt_id] != pred_id:
                id_switches += 1
            last_match_for_gt[gt_id] = pred_id

        per_frame_rows.append(
            {
                "frame": frame,
                "gt_count": len(gt_f),
                "pred_count": len(pred_f),
                "tp": frame_tp,
                "fp": frame_fp,
                "fn": frame_fn,
            }
        )

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    mota_like = 1.0 - ((fn + fp + id_switches) / total_gt) if total_gt else 0.0

    # Approximate IDF1:
    # Build global best one-to-one assignment between GT identities and predicted identities
    # using counts of matched detections across frames.
    gt_ids = sorted(gt["gt_track_id"].unique())
    pred_ids = sorted(pred["pred_track_id"].unique())

    idtp = 0
    if gt_ids and pred_ids:
        gt_index = {gid: i for i, gid in enumerate(gt_ids)}
        pred_index = {pid: j for j, pid in enumerate(pred_ids)}

        score = np.zeros((len(gt_ids), len(pred_ids)), dtype=float)
        for (gid, pid), count in pair_counts.items():
            score[gt_index[gid], pred_index[pid]] = count

        row_ind, col_ind = linear_sum_assignment(-score)
        idtp = int(score[row_ind, col_ind].sum())

    idfp = total_pred - idtp
    idfn = total_gt - idtp
    idf1_like = (2 * idtp) / ((2 * idtp) + idfp + idfn) if ((2 * idtp) + idfp + idfn) else 0.0

    return {
        "total_gt": total_gt,
        "total_pred": total_pred,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "id_switches": id_switches,
        "precision": precision,
        "recall": recall,
        "mota_like": mota_like,
        "idtp_like": idtp,
        "idfp_like": idfp,
        "idfn_like": idfn,
        "idf1_like": idf1_like,
        "per_frame": per_frame_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Local KITTI-style MOT evaluator.")
    parser.add_argument("--label-file", type=Path, default=Path("data/kitti_tracking/training/label_02/0000.txt"))
    parser.add_argument("--tracks-csv", type=Path, default=Path("results/tracks/yolov8n_bytetrack_seq0000_tracks.csv"))
    parser.add_argument("--class-name", type=str, default="Car")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics.csv"))
    parser.add_argument("--summary-csv", type=Path, default=Path("results/tables/m4_eval_summary.csv"))
    parser.add_argument("--log-file", type=Path, default=Path("results/logs/m4_local_eval.txt"))
    parser.add_argument("--sequence", type=str, default="0000")
    args = parser.parse_args()

    gt = load_kitti_gt(args.label_file, args.class_name)
    pred = load_predictions(args.tracks_csv, args.class_name)

    results = evaluate(gt, pred, args.iou_threshold)

    args.metrics_csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    metric_row = {
        "sequence": args.sequence,
        "class_name": args.class_name,
        "iou_threshold": args.iou_threshold,
        "total_gt": results["total_gt"],
        "total_pred": results["total_pred"],
        "tp": results["tp"],
        "fp": results["fp"],
        "fn": results["fn"],
        "id_switches": results["id_switches"],
        "precision": results["precision"],
        "recall": results["recall"],
        "mota_like": results["mota_like"],
        "idf1_like": results["idf1_like"],
        "idtp_like": results["idtp_like"],
        "idfp_like": results["idfp_like"],
        "idfn_like": results["idfn_like"],
        "evaluator": "local_kitti_style_not_official_trackeval",
    }

    with args.metrics_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metric_row.keys()))
        writer.writeheader()
        writer.writerow(metric_row)

    pd.DataFrame([metric_row]).to_csv(args.summary_csv, index=False)

    log_lines = [
        "========== M4 LOCAL KITTI-STYLE EVALUATION ==========",
        f"label_file: {args.label_file}",
        f"tracks_csv: {args.tracks_csv}",
        f"class_name: {args.class_name}",
        f"iou_threshold: {args.iou_threshold}",
        "",
        "Important:",
        "These are local KITTI-style metrics, not official KITTI leaderboard metrics and not TrackEval HOTA yet.",
        "",
    ]

    for key, value in metric_row.items():
        log_lines.append(f"{key}: {value}")

    args.log_file.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("\n".join(log_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

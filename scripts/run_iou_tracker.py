
#!/usr/bin/env python3

from pathlib import Path
import argparse
import time
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def box_iou_matrix(a, b):
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)), dtype=float)

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    ax1, ay1, ax2, ay2 = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
    bx1, by1, bx2, by2 = b[:, 0], b[:, 1], b[:, 2], b[:, 3]

    inter_x1 = np.maximum(ax1[:, None], bx1[None, :])
    inter_y1 = np.maximum(ay1[:, None], by1[None, :])
    inter_x2 = np.minimum(ax2[:, None], bx2[None, :])
    inter_y2 = np.minimum(ay2[:, None], by2[None, :])

    inter_w = np.maximum(0.0, inter_x2 - inter_x1)
    inter_h = np.maximum(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h

    area_a = np.maximum(0.0, ax2 - ax1) * np.maximum(0.0, ay2 - ay1)
    area_b = np.maximum(0.0, bx2 - bx1) * np.maximum(0.0, by2 - by1)

    union = area_a[:, None] + area_b[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def run_iou_tracker(detections, iou_threshold=0.3, max_age=2):
    active = {}
    next_track_id = 1
    rows = []

    frames = sorted(detections["frame"].astype(int).unique())

    for frame in frames:
        t0 = time.perf_counter()

        frame_df = detections[detections["frame"].astype(int) == frame].copy()
        frame_df = frame_df.sort_values("confidence", ascending=False).reset_index(drop=True)

        det_boxes = frame_df[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)

        track_ids = list(active.keys())
        track_boxes = np.asarray([active[tid]["box"] for tid in track_ids], dtype=float) if track_ids else np.empty((0, 4))

        matches = []
        unmatched_dets = set(range(len(frame_df)))
        unmatched_tracks = set(track_ids)

        if len(track_ids) > 0 and len(frame_df) > 0:
            ious = box_iou_matrix(track_boxes, det_boxes)
            cost = 1.0 - ious
            tr_idx, det_idx = linear_sum_assignment(cost)

            for ti, di in zip(tr_idx, det_idx):
                iou = ious[ti, di]
                if iou >= iou_threshold:
                    tid = track_ids[ti]
                    matches.append((tid, di))
                    unmatched_dets.discard(di)
                    unmatched_tracks.discard(tid)

        for tid, di in matches:
            box = det_boxes[di]
            active[tid] = {"box": box, "last_frame": frame}

        for di in sorted(unmatched_dets):
            tid = next_track_id
            next_track_id += 1
            box = det_boxes[di]
            active[tid] = {"box": box, "last_frame": frame}
            matches.append((tid, di))

        expired = []
        for tid, state in active.items():
            if frame - int(state["last_frame"]) > max_age:
                expired.append(tid)
        for tid in expired:
            active.pop(tid, None)

        latency_ms = (time.perf_counter() - t0) * 1000.0

        for tid, di in sorted(matches, key=lambda x: x[1]):
            r = frame_df.iloc[di]
            rows.append(
                {
                    "sequence": int(r["sequence"]),
                    "frame": int(r["frame"]),
                    "image_name": r["image_name"],
                    "track_id": int(tid),
                    "class_id": int(r["class_id"]),
                    "class_name": r["class_name"],
                    "confidence": float(r["confidence"]),
                    "x1": float(r["x1"]),
                    "y1": float(r["y1"]),
                    "x2": float(r["x2"]),
                    "y2": float(r["y2"]),
                    "latency_ms": latency_ms,
                }
            )

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detections-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--class-name", default="car")
    parser.add_argument("--iou-threshold", type=float, default=0.3)
    parser.add_argument("--max-age", type=int, default=2)
    args = parser.parse_args()

    det = pd.read_csv(args.detections_csv)
    det = det[det["class_name"].str.lower() == args.class_name.lower()].copy()

    tracks = run_iou_tracker(det, iou_threshold=args.iou_threshold, max_age=args.max_age)

    out = Path(args.output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    tracks.to_csv(out, index=False)

    print(f"input_detections: {len(det)}")
    print(f"output_tracks: {len(tracks)}")
    print(f"unique_track_ids: {tracks.track_id.nunique() if len(tracks) else 0}")
    print(f"wrote: {out}")


if __name__ == "__main__":
    main()

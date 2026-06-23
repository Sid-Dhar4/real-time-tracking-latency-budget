
#!/usr/bin/env python3

from pathlib import Path
import shutil
import pandas as pd


def export_tracker_file(seq, tracks_csv, out_file):
    df = pd.read_csv(tracks_csv)
    df = df[df["class_name"].str.lower() == "car"].copy()
    df = df.sort_values(["frame", "track_id"])

    out_file.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for _, r in df.iterrows():
        frame = int(r["frame"])
        tid = int(r["track_id"])
        cls = "car"
        trunc = -1
        occ = -1
        alpha = -10
        x1 = float(r["x1"])
        y1 = float(r["y1"])
        x2 = float(r["x2"])
        y2 = float(r["y2"])
        h = -1
        w = -1
        l = -1
        x = -1000
        y = -1000
        z = -1000
        ry = -10
        score = float(r["confidence"])

        line = (
            f"{frame} {tid} {cls} {trunc} {occ} {alpha} "
            f"{x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} "
            f"{h} {w} {l} {x} {y} {z} {ry} {score:.6f}"
        )
        lines.append(line)

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def main():
    gt_root = Path("external/TrackEval/data/gt/kitti/kitti_2d_box_train")
    tracker_root = Path("external/TrackEval/data/trackers/kitti/kitti_2d_box_train/yolov8n_bytetrack")
    tracker_data = tracker_root / "data"

    label_out = gt_root / "label_02"
    label_out.mkdir(parents=True, exist_ok=True)
    tracker_data.mkdir(parents=True, exist_ok=True)

    seqs = {
        "0000": {
            "length": 154,
            "gt": Path("data/kitti_tracking/training/label_02/0000.txt"),
            "tracks": Path("results/tracks/yolov8n_bytetrack_seq0000_tracks.csv"),
        },
        "0001": {
            "length": 447,
            "gt": Path("data/kitti_tracking/training/label_02/0001.txt"),
            "tracks": Path("results/tracks/yolov8n_bytetrack_seq0001_tracks.csv"),
        },
    }

    seqmap_lines = []
    for seq, info in seqs.items():
        shutil.copyfile(info["gt"], label_out / f"{seq}.txt")
        n = export_tracker_file(seq, info["tracks"], tracker_data / f"{seq}.txt")
        seqmap_lines.append("{} empty 000000 {}".format(seq, info["length"]))
        print(f"exported seq={seq} tracker_rows={n}")

    (gt_root / "evaluate_tracking.seqmap.training").write_text("\n".join(seqmap_lines) + "\n", encoding="utf-8")

    print(f"wrote_gt_root: {gt_root}")
    print(f"wrote_tracker_root: {tracker_root}")
    print("wrote_seqmap: {}".format(gt_root / "evaluate_tracking.seqmap.training"))


if __name__ == "__main__":
    main()

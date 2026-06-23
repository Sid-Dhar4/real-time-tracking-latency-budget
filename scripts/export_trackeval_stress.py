
#!/usr/bin/env python3

from pathlib import Path
import shutil
import pandas as pd


def write_tracker_file(df, out_file):
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df = df[df["class_name"].str.lower() == "car"].copy()
    df = df.sort_values(["frame", "track_id"])

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

        lines.append(
            f"{frame} {tid} {cls} {trunc} {occ} {alpha} "
            f"{x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} "
            f"{h} {w} {l} {x} {y} {z} {ry} {score:.6f}"
        )

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def main():
    gt_root = Path("external/TrackEval/data/gt/kitti/kitti_2d_box_train")
    label_out = gt_root / "label_02"
    label_out.mkdir(parents=True, exist_ok=True)

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

    for seq, info in seqs.items():
        shutil.copyfile(info["gt"], label_out / f"{seq}.txt")

    seqmap = "\n".join(
        "{} empty 000000 {}".format(seq, info["length"])
        for seq, info in seqs.items()
    ) + "\n"
    (gt_root / "evaluate_tracking.seqmap.training").write_text(seqmap, encoding="utf-8")

    tracker_root = Path("external/TrackEval/data/trackers/kitti/kitti_2d_box_train")

    variants = {
        "yolov8n_bytetrack": None,
        "yolov8n_bytetrack_drop_every_5": 5,
        "yolov8n_bytetrack_drop_every_3": 3,
        "yolov8n_bytetrack_drop_every_2": 2,
    }

    rows = []

    for variant, drop_n in variants.items():
        for seq, info in seqs.items():
            df = pd.read_csv(info["tracks"])
            original_rows = len(df)

            if drop_n is not None:
                df = df[df["frame"].astype(int) % drop_n != 0].copy()

            kept_rows = len(df)
            out_file = tracker_root / variant / "data" / f"{seq}.txt"
            written = write_tracker_file(df, out_file)

            rows.append(
                {
                    "variant": variant,
                    "sequence": seq,
                    "drop_every_n": "none" if drop_n is None else drop_n,
                    "original_rows": original_rows,
                    "kept_rows": kept_rows,
                    "written_rows": written,
                }
            )

            print(f"variant={variant} seq={seq} written_rows={written}")

    out = Path("results/tables/m14_stress_export_summary.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

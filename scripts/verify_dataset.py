#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def count_images(seq_dir: Path) -> int:
    if not seq_dir.exists():
        return 0
    return len(sorted(seq_dir.glob("*.png")))


def count_label_lines(label_file: Path) -> int:
    if not label_file.exists():
        return 0
    with label_file.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify KITTI tracking dataset structure.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/kitti_tracking"),
        help="KITTI tracking dataset root.",
    )
    parser.add_argument(
        "--sequences",
        nargs="+",
        default=["0000"],
        help="Sequence IDs to verify.",
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("results/tables/dataset_summary.csv"),
        help="Output CSV summary path.",
    )
    args = parser.parse_args()

    root = args.root
    image_root = root / "training" / "image_02"
    label_root = root / "training" / "label_02"
    calib_root = root / "training" / "calib"

    required_dirs = [root, image_root, label_root, calib_root]
    missing_dirs = [str(p) for p in required_dirs if not p.exists()]

    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for seq in args.sequences:
        seq_img_dir = image_root / seq
        label_file = label_root / f"{seq}.txt"
        calib_file = calib_root / f"{seq}.txt"

        image_count = count_images(seq_img_dir)
        label_count = count_label_lines(label_file)

        rows.append(
            {
                "sequence": seq,
                "image_dir": str(seq_img_dir),
                "label_file": str(label_file),
                "calib_file": str(calib_file),
                "image_dir_exists": seq_img_dir.exists(),
                "label_file_exists": label_file.exists(),
                "calib_file_exists": calib_file.exists(),
                "num_images": image_count,
                "num_label_lines": label_count,
            }
        )

    with args.summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sequence",
                "image_dir",
                "label_file",
                "calib_file",
                "image_dir_exists",
                "label_file_exists",
                "calib_file_exists",
                "num_images",
                "num_label_lines",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("========== KITTI TRACKING DATASET VERIFICATION ==========")
    print(f"Root: {root}")

    if missing_dirs:
        print("\nMissing required directories:")
        for p in missing_dirs:
            print(f"  - {p}")
    else:
        print("\nRequired root directories exist.")

    print("\nSequence summary:")
    for row in rows:
        print(
            f"  seq={row['sequence']} "
            f"images={row['num_images']} "
            f"label_lines={row['num_label_lines']} "
            f"image_dir_exists={row['image_dir_exists']} "
            f"label_exists={row['label_file_exists']} "
            f"calib_exists={row['calib_file_exists']}"
        )

    print(f"\nWrote summary CSV: {args.summary_csv}")

    all_ok = (
        not missing_dirs
        and all(row["image_dir_exists"] for row in rows)
        and all(row["label_file_exists"] for row in rows)
        and all(row["calib_file_exists"] for row in rows)
        and all(row["num_images"] > 0 for row in rows)
    )

    if all_ok:
        print("\nDATASET CHECK: PASS")
        return 0

    print("\nDATASET CHECK: NOT READY")
    print("This is okay if you have not downloaded or placed KITTI tracking data yet.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

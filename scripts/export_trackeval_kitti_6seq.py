#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import shutil

spec = importlib.util.spec_from_file_location("export_trackeval_kitti", Path("scripts/export_trackeval_kitti.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
export_tracker_file = module.export_tracker_file

SEQ_LENGTHS = {
    "0000": 154,
    "0001": 447,
    "0002": 233,
    "0003": 144,
    "0004": 314,
    "0005": 297,
}

def main():
    gt_root = Path("external/TrackEval/data/gt/kitti/kitti_2d_box_train")
    label_out = gt_root / "label_02"
    tracker_root = Path("external/TrackEval/data/trackers/kitti/kitti_2d_box_train/yolov8n_bytetrack_6seq")
    tracker_data = tracker_root / "data"
    label_out.mkdir(parents=True, exist_ok=True)
    tracker_data.mkdir(parents=True, exist_ok=True)

    seqmap_lines = []
    for seq, length in SEQ_LENGTHS.items():
        gt_src = Path("data/kitti_tracking/training/label_02") / f"{seq}.txt"
        track_src = Path("results/tracks") / f"yolov8n_bytetrack_seq{seq}_tracks.csv"
        shutil.copyfile(gt_src, label_out / f"{seq}.txt")
        n = export_tracker_file(seq, track_src, tracker_data / f"{seq}.txt")
        seqmap_lines.append("{} empty 000000 {}".format(seq, length))
        print("exported seq={} rows={}".format(seq, n))

    seqmap = gt_root / "evaluate_tracking.seqmap.training"
    seqmap.write_text("\n".join(seqmap_lines) + "\n", encoding="utf-8")
    print("wrote {}".format(seqmap))
    print("wrote {}".format(tracker_root))

if __name__ == "__main__":
    main()

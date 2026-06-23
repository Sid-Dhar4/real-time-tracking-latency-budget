#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

summary_path = Path("results/trackeval_6seq/m21_car_summary.txt")
detailed_path = Path("results/trackeval_6seq/m21_car_detailed.csv")

summary_lines = [x.strip() for x in summary_path.read_text().splitlines() if x.strip()]
headers = summary_lines[0].split()
values = summary_lines[1].split()
combined = dict(zip(headers, values))

df = pd.read_csv(detailed_path)
rows = []
for _, r in df.iterrows():
    seq_raw = str(r["seq"])
    if seq_raw == "COMBINED":
        continue
    seq = seq_raw.zfill(4) if seq_raw.isdigit() else seq_raw
    rows.append({
        "sequence": seq,
        "HOTA": float(r["HOTA___AUC"]) * 100.0,
        "MOTA": float(r["MOTA"]) * 100.0,
        "IDF1": float(r["IDF1"]) * 100.0,
        "CLR_Re": float(r["CLR_Re"]) * 100.0,
        "CLR_Pr": float(r["CLR_Pr"]) * 100.0,
        "IDSW": int(float(r["IDSW"])),
        "Dets": int(float(r["Dets"])),
        "GT_Dets": int(float(r["GT_Dets"])),
        "IDs": int(float(r["IDs"])),
        "GT_IDs": int(float(r["GT_IDs"])),
    })

out = pd.DataFrame(rows)
out.loc[len(out)] = {
    "sequence": "COMBINED",
    "HOTA": float(combined["HOTA"]),
    "MOTA": float(combined["MOTA"]),
    "IDF1": float(combined["IDF1"]),
    "CLR_Re": float(combined["CLR_Re"]),
    "CLR_Pr": float(combined["CLR_Pr"]),
    "IDSW": int(float(combined["IDSW"])),
    "Dets": int(float(combined["Dets"])),
    "GT_Dets": int(float(combined["GT_Dets"])),
    "IDs": int(float(combined["IDs"])),
    "GT_IDs": int(float(combined["GT_IDs"])),
}

out.to_csv("results/tables/m21_trackeval_6seq_summary.csv", index=False)

plot_df = out[out["sequence"] != "COMBINED"].copy()
x = range(len(plot_df))
plt.figure()
plt.plot(list(x), plot_df["HOTA"], marker="o", label="HOTA")
plt.plot(list(x), plot_df["MOTA"], marker="o", label="MOTA")
plt.plot(list(x), plot_df["IDF1"], marker="o", label="IDF1")
plt.xticks(list(x), plot_df["sequence"])
plt.ylabel("Metric score")
plt.title("TrackEval KITTI metrics across 6 sequences")
plt.legend()
plt.tight_layout()
plt.savefig("results/plots/m21_trackeval_6seq_metrics.png", dpi=160)
plt.close()

report = "# Six-Sequence TrackEval KITTI Benchmark\n\n"
report += "Native TrackEval KITTI 2D box evaluation was run for class `car` on KITTI tracking sequences `0000` through `0005`.\n\n"
report += "## Combined results\n\n"
report += "- HOTA: `{:.3f}`\n".format(float(combined["HOTA"]))
report += "- MOTA: `{:.3f}`\n".format(float(combined["MOTA"]))
report += "- IDF1: `{:.3f}`\n".format(float(combined["IDF1"]))
report += "- GT detections: `{}`\n".format(int(float(combined["GT_Dets"])))
report += "- Tracker detections: `{}`\n".format(int(float(combined["Dets"])))
report += "- ID switches: `{}`\n\n".format(int(float(combined["IDSW"])))
report += "## Per-sequence results\n\n"
report += "| sequence | HOTA | MOTA | IDF1 | IDSW | Dets | GT Dets |\n"
report += "| -------- | ---- | ---- | ---- | ---- | ---- | ------- |\n"
for _, r in out[out["sequence"] != "COMBINED"].iterrows():
    report += "| {} | {:.3f} | {:.3f} | {:.3f} | {} | {} | {} |\n".format(r["sequence"], r["HOTA"], r["MOTA"], r["IDF1"], int(r["IDSW"]), int(r["Dets"]), int(r["GT_Dets"]))
report += "\n## Notes\n\n"
report += "- This is a local TrackEval evaluation on KITTI training sequences, not a public KITTI leaderboard submission.\n"
report += "- The detector uses pretrained YOLOv8n weights.\n"
report += "- This expands benchmark coverage from 2 sequences to 6 sequences.\n\n"
report += "## Artifacts\n\n"
report += "- `results/tables/m21_trackeval_6seq_summary.csv`\n"
report += "- `results/plots/m21_trackeval_6seq_metrics.png`\n"
report += "- `results/trackeval_6seq/m21_car_summary.txt`\n"
report += "- `results/trackeval_6seq/m21_car_detailed.csv`\n"
Path("reports/trackeval_6seq_results.md").write_text(report)

print(out.to_string(index=False))
print("wrote results/tables/m21_trackeval_6seq_summary.csv")
print("wrote results/plots/m21_trackeval_6seq_metrics.png")
print("wrote reports/trackeval_6seq_results.md")

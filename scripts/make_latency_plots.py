
#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def load_frame_latencies(path):
    df = pd.read_csv(path)
    return df.groupby("frame")["latency_ms"].first().sort_index()


def main():
    specs = [
        ("0000", "detector", "results/detections/yolov8n_seq0000_detections.csv"),
        ("0000", "tracker", "results/tracks/yolov8n_bytetrack_seq0000_tracks.csv"),
        ("0001", "detector", "results/detections/yolov8n_seq0001_detections.csv"),
        ("0001", "tracker", "results/tracks/yolov8n_bytetrack_seq0001_tracks.csv"),
    ]

    out_dir = Path("results/plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    warmup = 5
    rows = []

    plt.figure()
    for seq, stage, path in specs:
        lat = load_frame_latencies(path)
        used = lat.iloc[warmup:] if len(lat) > warmup else lat
        label = f"seq{seq} {stage}"
        plt.hist(used, bins=30, alpha=0.45, label=label)
        rows.append(
            {
                "sequence": seq,
                "stage": stage,
                "mean_ms": used.mean(),
                "p95_ms": used.quantile(0.95),
                "p99_ms": used.quantile(0.99),
            }
        )

    plt.xlabel("Latency per frame (ms)")
    plt.ylabel("Frame count")
    plt.title("Warmup-excluded CPU latency distributions")
    plt.legend()
    plt.tight_layout()
    hist_path = out_dir / "m12_latency_histogram.png"
    plt.savefig(hist_path, dpi=160)
    plt.close()

    summary = pd.DataFrame(rows)
    labels = [f"{r.sequence}-{r.stage}" for _, r in summary.iterrows()]

    plt.figure()
    x = range(len(summary))
    plt.bar(x, summary["mean_ms"])
    plt.xticks(list(x), labels, rotation=30, ha="right")
    plt.ylabel("Mean latency per frame (ms)")
    plt.title("Mean CPU latency by sequence and stage")
    plt.tight_layout()
    bar_path = out_dir / "m12_latency_summary_bar.png"
    plt.savefig(bar_path, dpi=160)
    plt.close()

    report = Path("reports/runtime_analysis.md")
    lines = [
        "# Runtime Analysis",
        "",
        "This report summarizes warmup-excluded CPU latency for detector and tracker outputs.",
        "",
        "Warmup policy: first 5 frames excluded.",
        "",
        "## Plots",
        "",
        "- `results/plots/m12_latency_histogram.png`",
        "- `results/plots/m12_latency_summary_bar.png`",
        "",
        "## Summary",
        "",
        "| sequence | stage | mean ms | p95 ms | p99 ms |",
        "| -------- | ----- | ------- | ------ | ------ |",
    ]

    for _, r in summary.iterrows():
        lines.append(f"| {r.sequence} | {r.stage} | {r.mean_ms:.2f} | {r.p95_ms:.2f} | {r.p99_ms:.2f} |")

    lines += [
        "",
        "## Caveats",
        "",
        "- These are CPU measurements.",
        "- NVIDIA GPU benchmarking is future work after driver fix.",
        "- Latency values are computed from saved per-frame CSV outputs.",
    ]

    report.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {hist_path}")
    print(f"wrote {bar_path}")
    print(f"wrote {report}")


if __name__ == "__main__":
    main()

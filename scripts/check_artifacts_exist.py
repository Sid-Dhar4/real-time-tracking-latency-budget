#!/usr/bin/env python3

from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "docs/final_project_summary.md",
    "reports/trackeval_results.md",
    "reports/trackeval_stress_test.md",
    "reports/tracker_comparison.md",
    "reports/runtime_analysis.md",
    "reports/demo_notes.md",
    "results/trackeval/m13_car_summary.txt",
    "results/tables/m14_trackeval_stress_summary.csv",
    "results/tables/m15_tracker_comparison.csv",
    "results/plots/m12_latency_histogram.png",
    "results/plots/m14_trackeval_stress_metrics.png",
    "results/plots/m15_tracker_comparison_metrics.png",
    "results/videos/m11_seq0001_demo_overlay.mp4",
]

FORBIDDEN_README_PHRASES = [
    "Tests will cover",
    "not official TrackEval HOTA yet",
    "Not measured yet",
    "Not started yet",
    "GPU benchmark complete",
    "official KITTI leaderboard",
]

def main():
    missing = [p for p in REQUIRED_FILES if not Path(p).is_file()]
    if missing:
        print("Missing required artifacts:")
        for p in missing:
            print(f"  - {p}")
        raise SystemExit(1)

    readme = Path("README.md").read_text(encoding="utf-8")
    bad = [phrase for phrase in FORBIDDEN_README_PHRASES if phrase in readme]
    if bad:
        print("Forbidden stale/overclaim README phrases found:")
        for phrase in bad:
            print(f"  - {phrase}")
        raise SystemExit(1)

    print("Artifact and stale-claim checks passed.")

if __name__ == "__main__":
    main()

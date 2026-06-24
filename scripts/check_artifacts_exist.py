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
    "media/tracking_latency_teaser.gif",
    "media/tracking_latency_demo.mp4",
    "media/tracking_latency_poster.jpg",
    "reports/trackeval_6seq_results.md",
    "results/tables/m21_trackeval_6seq_summary.csv",
    "results/plots/m21_trackeval_6seq_metrics.png",
    "results/trackeval_6seq/m21_car_summary.txt",
    "results/tables/m26_ros2_latency_summary.csv",
    "scripts/ros2_diagnostic_latency_probe.py",
    "reports/ros2_latency_probe.md",
    "reports/ros2_typed_topics.md",
    "reports/ros2_debug_image_replay.md",
    "media/tracking_debug_image_sample.jpg",
    "ros2/ros2_tracking_latency/ros2_tracking_latency/kitti_debug_image_replay_node.py",
    "docs/release_notes_v1.0.0.md",
    "scripts/check_ros2_message_helpers.py",
    "scripts/compute_track_risk.py",
    "reports/track_reliability_risk.md",
    "results/tables/m33_track_risk_summary.csv",
    "results/tables/m33_top_risky_tracks.csv",
    "reports/track_risk_validation.md",
    "results/tables/m34_risk_bucket_summary.csv",
    "results/plots/m34_risk_bucket_summary.png",
    "reports/runtime_environment_audit.md",
    "results/tables/m35_runtime_environment_audit.csv",
    "scripts/benchmark_cpu_gpu_latency.py",
    "reports/cpu_gpu_latency_benchmark.md",
    "results/tables/m36_cpu_gpu_latency_raw.csv",
    "results/tables/m36_cpu_gpu_latency_summary.csv",
    "results/plots/m36_cpu_gpu_latency_comparison.png",
    "docs/reproduction_matrix.md",
    "scripts/check_ros2_workspace.sh",
    "reports/ros2_workspace_smoke_check.md",
    "scripts/check_ros2_end_to_end_topics.sh",
    "reports/ros2_end_to_end_topic_smoke_check.md",
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

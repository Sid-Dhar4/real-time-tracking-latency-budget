#!/usr/bin/env python3
import argparse
import csv
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from diagnostic_msgs.msg import DiagnosticArray


def diagnostic_values(msg):
    values = {}
    for status in msg.status:
        for kv in status.values:
            values[str(kv.key)] = str(kv.value)
    return values


class DiagnosticLatencyProbe(Node):
    def __init__(self, output_csv, max_samples, timeout_sec):
        super().__init__("diagnostic_latency_probe")
        self.output_csv = Path(output_csv)
        self.max_samples = int(max_samples)
        self.timeout_sec = float(timeout_sec)
        self.start_perf = time.perf_counter()
        self.rows = []
        self.done = False
        self.sub = self.create_subscription(DiagnosticArray, "/tracking/diagnostics", self.callback, 10)
        self.timer = self.create_timer(0.25, self.check_timeout)
        self.get_logger().info("Listening on /tracking/diagnostics")

    def callback(self, msg):
        if self.done:
            return
        recv_now = self.get_clock().now()
        recv_sec = recv_now.nanoseconds / 1e9
        stamp_sec = float(msg.header.stamp.sec) + float(msg.header.stamp.nanosec) * 1e-9
        receive_latency_ms = (recv_sec - stamp_sec) * 1000.0
        values = diagnostic_values(msg)
        row = {
            "sample_idx": len(self.rows),
            "recv_time_sec": recv_sec,
            "msg_stamp_sec": stamp_sec,
            "ros_receive_latency_ms": receive_latency_ms,
            "sequence": values.get("sequence", ""),
            "frame": values.get("frame", ""),
            "num_tracks": values.get("num_tracks", ""),
            "fps": values.get("fps", ""),
            "publish_latency_ms": values.get("publish_latency_ms", ""),
            "source_csv": values.get("source_csv", ""),
        }
        self.rows.append(row)
        if len(self.rows) >= self.max_samples:
            self.finish("max samples reached")

    def check_timeout(self):
        if self.done:
            return
        if time.perf_counter() - self.start_perf > self.timeout_sec:
            self.finish("timeout reached")

    def finish(self, reason):
        self.done = True
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "sample_idx",
            "recv_time_sec",
            "msg_stamp_sec",
            "ros_receive_latency_ms",
            "sequence",
            "frame",
            "num_tracks",
            "fps",
            "publish_latency_ms",
            "source_csv",
        ]
        with self.output_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(self.rows)
        self.get_logger().info("{}; wrote {} rows to {}".format(reason, len(self.rows), self.output_csv))
        rclpy.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-csv", default="results/tables/m26_ros2_latency_probe.csv")
    parser.add_argument("--max-samples", type=int, default=30)
    parser.add_argument("--timeout-sec", type=float, default=20.0)
    args = parser.parse_args()
    rclpy.init()
    node = DiagnosticLatencyProbe(args.output_csv, args.max_samples, args.timeout_sec)
    rclpy.spin(node)


if __name__ == "__main__":
    main()

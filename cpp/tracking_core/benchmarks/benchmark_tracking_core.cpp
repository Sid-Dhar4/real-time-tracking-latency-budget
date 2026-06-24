#include "tracking_core/iou.hpp"
#include "tracking_core/risk_score.hpp"

#include <chrono>
#include <iostream>
#include <vector>

int main() {
  using clock = std::chrono::steady_clock;

  std::vector<tracking_core::Box> detections;
  std::vector<tracking_core::Box> tracks;

  for (int i = 0; i < 128; ++i) {
    const double x = static_cast<double>(i * 4);
    detections.push_back({x, x, x + 40.0, x + 40.0});
    tracks.push_back({x + 2.0, x + 2.0, x + 42.0, x + 42.0});
  }

  const int iterations = 1000;
  std::size_t total_matches = 0;

  const auto start = clock::now();

  for (int iter = 0; iter < iterations; ++iter) {
    const auto matches = tracking_core::greedy_associate(detections, tracks, 0.5);
    total_matches += matches.size();

    for (const auto& det : detections) {
      const double box_area = tracking_core::area(det);
      const auto risk = tracking_core::compute_risk(
          tracking_core::RiskInputs{
              .confidence = 0.75,
              .box_area = box_area,
              .min_area = 100.0,
              .max_area = 10000.0,
              .near_image_border = false,
              .center_jump_per_frame_px = 5.0,
              .max_center_jump_per_frame_px = 100.0,
              .track_length = 8,
          });

      if (risk.risk_score < 0.0) {
        return 1;
      }
    }
  }

  const auto elapsed = std::chrono::duration<double, std::milli>(clock::now() - start).count();
  const double per_iteration_ms = elapsed / static_cast<double>(iterations);

  std::cout << "iterations: " << iterations << "\n";
  std::cout << "detections: " << detections.size() << "\n";
  std::cout << "tracks: " << tracks.size() << "\n";
  std::cout << "total_matches: " << total_matches << "\n";
  std::cout << "total_ms: " << elapsed << "\n";
  std::cout << "per_iteration_ms: " << per_iteration_ms << "\n";

  return 0;
}

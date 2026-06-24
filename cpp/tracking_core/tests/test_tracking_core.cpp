#include "tracking_core/iou.hpp"
#include "tracking_core/risk_score.hpp"
#include "tracking_core/track_state.hpp"

#include <cassert>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>

using tracking_core::Box;
using tracking_core::RiskInputs;
using tracking_core::TrackLifecycle;
using tracking_core::TrackState;
using tracking_core::compute_risk;
using tracking_core::greedy_associate;
using tracking_core::iou;
using tracking_core::risk_level;
using tracking_core::safety_state;

namespace {

bool near(double a, double b, double eps = 1e-6) {
  return std::abs(a - b) < eps;
}

void test_iou_identity() {
  const Box a{0.0, 0.0, 10.0, 10.0};
  assert(near(iou(a, a), 1.0));
}

void test_iou_no_overlap() {
  const Box a{0.0, 0.0, 10.0, 10.0};
  const Box b{20.0, 20.0, 30.0, 30.0};
  assert(near(iou(a, b), 0.0));
}

void test_greedy_association() {
  const std::vector<Box> detections{
      {0.0, 0.0, 10.0, 10.0},
      {100.0, 100.0, 120.0, 120.0},
  };
  const std::vector<Box> tracks{
      {1.0, 1.0, 11.0, 11.0},
      {101.0, 101.0, 121.0, 121.0},
  };

  const auto matches = greedy_associate(detections, tracks, 0.5);
  assert(matches.size() == 2);
  assert(matches[0].iou >= 0.5);
  assert(matches[1].iou >= 0.5);
}

void test_track_lifecycle() {
  TrackState state(7, Box{0.0, 0.0, 10.0, 10.0});

  assert(state.id == 7);
  assert(state.lifecycle == TrackLifecycle::Tentative);
  assert(state.hits == 1);
  assert(state.misses == 0);

  state.update(Box{2.0, 0.0, 12.0, 10.0});
  assert(state.lifecycle == TrackLifecycle::Confirmed);
  assert(state.hits == 2);
  assert(state.misses == 0);
  assert(near(state.velocity_x, 2.0));
  assert(near(state.velocity_y, 0.0));

  state.mark_missed(2);
  assert(state.lifecycle == TrackLifecycle::Lost);
  assert(state.misses == 1);

  state.mark_missed(2);
  state.mark_missed(2);
  assert(state.lifecycle == TrackLifecycle::Deleted);
}

void test_risk_score_ordering() {
  const auto low = compute_risk(RiskInputs{
      .confidence = 0.95,
      .box_area = 9000.0,
      .min_area = 1000.0,
      .max_area = 10000.0,
      .near_image_border = false,
      .center_jump_per_frame_px = 1.0,
      .max_center_jump_per_frame_px = 100.0,
      .track_length = 20,
  });

  const auto high = compute_risk(RiskInputs{
      .confidence = 0.30,
      .box_area = 1200.0,
      .min_area = 1000.0,
      .max_area = 10000.0,
      .near_image_border = true,
      .center_jump_per_frame_px = 75.0,
      .max_center_jump_per_frame_px = 100.0,
      .track_length = 1,
  });

  assert(low.risk_score < high.risk_score);
  assert(std::string(risk_level(low.risk_score)) == "low");
  assert(std::string(risk_level(high.risk_score)) == "high");
}

void test_safety_state() {
  assert(std::string(safety_state(0.20, 0)) == "nominal");
  assert(std::string(safety_state(0.50, 1)) == "caution");
  assert(std::string(safety_state(0.70, 1)) == "degraded");
}

}  // namespace

int main() {
  test_iou_identity();
  test_iou_no_overlap();
  test_greedy_association();
  test_track_lifecycle();
  test_risk_score_ordering();
  test_safety_state();

  std::cout << "C++ tracking core tests passed." << std::endl;
  return 0;
}

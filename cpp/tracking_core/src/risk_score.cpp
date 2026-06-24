#include "tracking_core/risk_score.hpp"

#include <algorithm>

namespace tracking_core {

namespace {

double clamp01(double x) {
  return std::max(0.0, std::min(1.0, x));
}

double normalize01(double x, double min_value, double max_value) {
  if (max_value <= min_value) {
    return 0.0;
  }
  return clamp01((x - min_value) / (max_value - min_value));
}

}  // namespace

RiskBreakdown compute_risk(const RiskInputs& inputs) {
  RiskBreakdown out;

  out.low_confidence_risk = clamp01(1.0 - inputs.confidence);
  out.small_box_risk = clamp01(1.0 - normalize01(inputs.box_area, inputs.min_area, inputs.max_area));
  out.border_risk = inputs.near_image_border ? 1.0 : 0.0;
  out.motion_jump_risk = normalize01(inputs.center_jump_per_frame_px, 0.0, inputs.max_center_jump_per_frame_px);

  const int safe_track_length = std::max(1, inputs.track_length);
  out.short_track_risk = clamp01(1.0 / static_cast<double>(safe_track_length));

  out.risk_score =
      0.25 * out.low_confidence_risk +
      0.20 * out.small_box_risk +
      0.15 * out.border_risk +
      0.25 * out.motion_jump_risk +
      0.15 * out.short_track_risk;

  out.risk_score = clamp01(out.risk_score);
  return out;
}

const char* risk_level(double risk_score) {
  if (risk_score >= 0.65) {
    return "high";
  }
  if (risk_score >= 0.45) {
    return "medium";
  }
  return "low";
}

const char* safety_state(double max_risk_score, int medium_or_high_tracks) {
  if (max_risk_score >= 0.65) {
    return "degraded";
  }
  if (medium_or_high_tracks > 0 || max_risk_score >= 0.45) {
    return "caution";
  }
  return "nominal";
}

}  // namespace tracking_core

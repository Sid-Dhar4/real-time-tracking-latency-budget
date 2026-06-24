#pragma once

namespace tracking_core {

struct RiskInputs {
  double confidence{1.0};
  double box_area{0.0};
  double min_area{0.0};
  double max_area{1.0};
  bool near_image_border{false};
  double center_jump_per_frame_px{0.0};
  double max_center_jump_per_frame_px{1.0};
  int track_length{1};
};

struct RiskBreakdown {
  double low_confidence_risk{0.0};
  double small_box_risk{0.0};
  double border_risk{0.0};
  double motion_jump_risk{0.0};
  double short_track_risk{0.0};
  double risk_score{0.0};
};

RiskBreakdown compute_risk(const RiskInputs& inputs);

const char* risk_level(double risk_score);
const char* safety_state(double max_risk_score, int medium_or_high_tracks);

}  // namespace tracking_core

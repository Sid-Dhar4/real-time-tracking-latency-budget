#pragma once

#include "tracking_core/iou.hpp"

namespace tracking_core {

enum class TrackLifecycle {
  Tentative,
  Confirmed,
  Lost,
  Deleted,
};

struct TrackState {
  int id{};
  Box box{};
  TrackLifecycle lifecycle{TrackLifecycle::Tentative};
  int age{0};
  int hits{0};
  int misses{0};
  double center_x{0.0};
  double center_y{0.0};
  double velocity_x{0.0};
  double velocity_y{0.0};

  TrackState() = default;
  TrackState(int track_id, const Box& initial_box);

  void update(const Box& new_box);
  void mark_missed(int max_misses_before_deleted = 3);
};

const char* lifecycle_name(TrackLifecycle state);

}  // namespace tracking_core

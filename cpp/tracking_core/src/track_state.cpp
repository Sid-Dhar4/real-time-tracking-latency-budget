#include "tracking_core/track_state.hpp"

namespace tracking_core {

namespace {

double center_x_from_box(const Box& box) {
  return 0.5 * (box.x1 + box.x2);
}

double center_y_from_box(const Box& box) {
  return 0.5 * (box.y1 + box.y2);
}

}  // namespace

TrackState::TrackState(int track_id, const Box& initial_box)
    : id(track_id), box(initial_box), lifecycle(TrackLifecycle::Tentative), age(1), hits(1), misses(0) {
  center_x = center_x_from_box(initial_box);
  center_y = center_y_from_box(initial_box);
}

void TrackState::update(const Box& new_box) {
  const double new_center_x = center_x_from_box(new_box);
  const double new_center_y = center_y_from_box(new_box);

  velocity_x = new_center_x - center_x;
  velocity_y = new_center_y - center_y;

  center_x = new_center_x;
  center_y = new_center_y;
  box = new_box;

  age += 1;
  hits += 1;
  misses = 0;

  if (hits >= 2) {
    lifecycle = TrackLifecycle::Confirmed;
  }
}

void TrackState::mark_missed(int max_misses_before_deleted) {
  age += 1;
  misses += 1;

  if (misses > max_misses_before_deleted) {
    lifecycle = TrackLifecycle::Deleted;
  } else {
    lifecycle = TrackLifecycle::Lost;
  }
}

const char* lifecycle_name(TrackLifecycle state) {
  switch (state) {
    case TrackLifecycle::Tentative:
      return "tentative";
    case TrackLifecycle::Confirmed:
      return "confirmed";
    case TrackLifecycle::Lost:
      return "lost";
    case TrackLifecycle::Deleted:
      return "deleted";
  }

  return "unknown";
}

}  // namespace tracking_core

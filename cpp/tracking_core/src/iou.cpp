#include "tracking_core/iou.hpp"

#include <algorithm>
#include <vector>

namespace tracking_core {

double area(const Box& box) {
  const double width = std::max(0.0, box.x2 - box.x1);
  const double height = std::max(0.0, box.y2 - box.y1);
  return width * height;
}

double iou(const Box& a, const Box& b) {
  const double ix1 = std::max(a.x1, b.x1);
  const double iy1 = std::max(a.y1, b.y1);
  const double ix2 = std::min(a.x2, b.x2);
  const double iy2 = std::min(a.y2, b.y2);

  const double intersection = area(Box{ix1, iy1, ix2, iy2});
  const double union_area = area(a) + area(b) - intersection;

  if (union_area <= 0.0) {
    return 0.0;
  }

  return intersection / union_area;
}

std::vector<Match> greedy_associate(
    const std::vector<Box>& detections,
    const std::vector<Box>& tracks,
    double iou_threshold) {
  std::vector<Match> candidates;

  for (int det_i = 0; det_i < static_cast<int>(detections.size()); ++det_i) {
    for (int trk_i = 0; trk_i < static_cast<int>(tracks.size()); ++trk_i) {
      const double score = iou(detections[det_i], tracks[trk_i]);
      if (score >= iou_threshold) {
        candidates.push_back(Match{det_i, trk_i, score});
      }
    }
  }

  std::sort(candidates.begin(), candidates.end(), [](const Match& a, const Match& b) {
    return a.iou > b.iou;
  });

  std::vector<bool> used_detections(detections.size(), false);
  std::vector<bool> used_tracks(tracks.size(), false);
  std::vector<Match> matches;

  for (const auto& candidate : candidates) {
    if (used_detections[candidate.detection_index] || used_tracks[candidate.track_index]) {
      continue;
    }

    used_detections[candidate.detection_index] = true;
    used_tracks[candidate.track_index] = true;
    matches.push_back(candidate);
  }

  return matches;
}

}  // namespace tracking_core

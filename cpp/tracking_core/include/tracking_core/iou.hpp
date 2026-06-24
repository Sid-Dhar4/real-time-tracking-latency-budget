#pragma once

#include <vector>

namespace tracking_core {

struct Box {
  double x1{};
  double y1{};
  double x2{};
  double y2{};
};

struct Match {
  int detection_index{};
  int track_index{};
  double iou{};
};

double area(const Box& box);
double iou(const Box& a, const Box& b);

std::vector<Match> greedy_associate(
    const std::vector<Box>& detections,
    const std::vector<Box>& tracks,
    double iou_threshold);

}  // namespace tracking_core

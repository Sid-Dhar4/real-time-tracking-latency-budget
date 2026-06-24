# Robot-Facing Risk / Safety Interface

This report documents the robot-facing reliability interface added to the ROS 2 tracking replay wrapper.

## Purpose

The project computes deterministic track-risk scores and validates them against local tracking failure diagnostics. This interface exposes that information as ROS 2 topics that a downstream planner, monitor, or safety layer could consume.

The goal is not to certify safety. The goal is to expose perception reliability signals in a robot-facing format.

## Topics

The track replay node publishes two additional topics:

- `/tracking/risk` as `std_msgs/msg/String`
- `/tracking/safety_status` as `std_msgs/msg/String`

These are JSON payloads for compatibility and easy inspection.

## Risk payload

`/tracking/risk` contains a per-frame summary:

- `sequence`
- `frame`
- `source_csv`
- `num_risk_rows`
- `max_risk_score`
- `mean_risk_score`
- `num_medium_risk_tracks`
- `num_high_risk_tracks`
- `num_medium_or_high_risk_tracks`
- `safety_state`
- `reason`

## Safety status payload

`/tracking/safety_status` contains the compact downstream-facing status:

- `sequence`
- `frame`
- `safety_state`
- `reason`
- `max_risk_score`
- `num_medium_or_high_risk_tracks`

## Safety states

The replay wrapper uses deterministic thresholds:

- `nominal`: all active tracks are below medium-risk threshold
- `caution`: one or more medium-risk tracks are active
- `degraded`: one or more high-risk tracks are active

## Latest local result

The ROS 2 end-to-end topic smoke check verified that the replay node publishes:

- `/tracking/status`
- `/tracking/objects`
- `/tracking/detections_2d`
- `/tracking/diagnostics`
- `/tracking/risk`
- `/tracking/safety_status`
- `/tracking/debug_image`

Observed safety payload example included `safety_state: caution` with reason `one or more medium-risk tracks active`.

## Claim boundary

This is a deterministic reliability diagnostic interface, not a certified safety controller. It does not command robot motion or make planning decisions. It exposes risk summaries so downstream autonomy software can decide how to react.

# Latency Tradeoff Report

This report summarizes CPU latency from saved detector/tracker outputs. The first 5 frames are excluded as warmup.

These are CPU-only measurements because NVIDIA driver support was not working through nvidia-smi during this project.

## Summary

| sequence | stage | frames used | mean ms | p50 ms | p90 ms | p95 ms | p99 ms | max ms | fps from mean |
| -------- | ----- | ----------- | ------- | ------ | ------ | ------ | ------ | ------ | ------------- |
| 0 | detector | 149 | 11.15 | 10.90 | 13.03 | 13.66 | 14.34 | 14.43 | 89.69 |
| 0 | tracker | 149 | 12.94 | 12.26 | 15.82 | 16.11 | 16.73 | 16.88 | 77.28 |
| 1 | detector | 442 | 12.58 | 11.93 | 14.89 | 15.43 | 16.06 | 16.81 | 79.50 |
| 1 | tracker | 442 | 13.31 | 12.90 | 15.52 | 16.17 | 17.66 | 19.06 | 75.14 |

## Caveats

- This is not a GPU benchmark.
- Latency is computed from saved CSV outputs, grouped by frame.
- The first 5 frames are excluded as warmup.
- Final deployment claims should use a dedicated benchmark script after GPU driver fix.

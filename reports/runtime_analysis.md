# Runtime Analysis

This report summarizes warmup-excluded CPU latency for detector and tracker outputs.

Warmup policy: first 5 frames excluded.

## Plots

- `results/plots/m12_latency_histogram.png`
- `results/plots/m12_latency_summary_bar.png`

## Summary

| sequence | stage | mean ms | p95 ms | p99 ms |
| -------- | ----- | ------- | ------ | ------ |
| 0000 | detector | 11.15 | 13.66 | 14.34 |
| 0000 | tracker | 12.94 | 16.11 | 16.73 |
| 0001 | detector | 12.58 | 15.43 | 16.06 |
| 0001 | tracker | 13.31 | 16.17 | 17.66 |

## Caveats

- These are CPU measurements.
- NVIDIA GPU benchmarking is future work after driver fix.
- Latency values are computed from saved per-frame CSV outputs.
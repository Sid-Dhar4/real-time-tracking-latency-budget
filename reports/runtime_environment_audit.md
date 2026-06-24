# Runtime Environment Audit

This report records the runtime environment used for the tracking latency benchmark.

## Result

The current environment supports the CPU benchmark path, but not a GPU benchmark path.

## GPU status

`nvidia-smi` is not able to communicate with the NVIDIA driver in this environment. PyTorch is installed as a CPU-only build and reports CUDA unavailable.

Therefore, this repository does **not** claim GPU latency numbers for this run.

## Why this matters

A real robotics latency benchmark should separate measured results from unavailable hardware paths. Reporting GPU latency without a working NVIDIA driver and CUDA-enabled PyTorch would be misleading.

## Current decision

- CPU latency benchmark: supported
- GPU latency benchmark: not run
- Future GPU benchmark requirement: working `nvidia-smi`, CUDA-enabled PyTorch, and a repeatable CPU-vs-GPU measurement script

## Audit table

See:

- `results/tables/m35_runtime_environment_audit.csv`

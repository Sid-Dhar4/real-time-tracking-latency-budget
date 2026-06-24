# Runtime Environment Audit

This report records the runtime environment used for the tracking latency benchmark.

## Result

The current environment supports the CPU benchmark path and CUDA-enabled PyTorch execution.

## GPU status

`nvidia-smi` is available and the NVIDIA kernel driver is active.

- GPU: `NVIDIA GeForce RTX 5060 Laptop GPU`
- NVIDIA driver: `595.71.05`
- GPU memory: `8151 MiB`
- PyTorch: `2.11.0+cu128`
- PyTorch CUDA runtime: `12.8`
- CUDA available in PyTorch: `True`
- CUDA tensor test: `ok (1024, 1024)`

## Benchmark claim boundary

This audit confirms that CUDA is available in the project environment. It does **not** by itself claim GPU latency numbers.

GPU latency numbers are reported separately in `reports/cpu_gpu_latency_benchmark.md`, after a controlled CPU-vs-GPU benchmark was run, saved, documented, and checked into the repository.

## Current decision

- CPU latency benchmark: supported
- CUDA PyTorch execution: supported
- GPU latency benchmark: ready to measure next
- GPU benchmark claim: not made yet

## Audit table

See:

- `results/tables/m35_runtime_environment_audit.csv`

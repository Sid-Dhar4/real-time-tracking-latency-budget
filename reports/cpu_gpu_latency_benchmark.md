# CPU vs GPU Latency Benchmark

This report measures YOLOv8n inference latency on KITTI tracking frames using both CPU and GPU execution in the project environment.

## Environment

The benchmark was run after CUDA-enabled PyTorch was verified in the `tracking-latency` conda environment.

- GPU: NVIDIA GeForce RTX 5060 Laptop GPU
- PyTorch CUDA runtime: 12.8
- Benchmark script: `scripts/benchmark_cpu_gpu_latency.py`
- Input config: `configs/detector/yolov8n.yaml`
- Frames measured per device: `100`
- Warmup frames per device: `5`

## Outputs

- `results/tables/m36_cpu_gpu_latency_raw.csv`
- `results/tables/m36_cpu_gpu_latency_summary.csv`
- `results/plots/m36_cpu_gpu_latency_comparison.png`

## Measured results

| Device | Mean latency ms | Median latency ms | P95 latency ms | FPS from mean | 30 Hz mean | 30 Hz p95 | 60 Hz mean | 60 Hz p95 |
| ------ | --------------- | ----------------- | -------------- | ------------- | ---------- | --------- | ---------- | --------- |
| CPU | 9.398 | 9.328 | 9.867 | 106.41 | True | True | True | True |
| GPU | 3.218 | 3.211 | 3.247 | 310.76 | True | True | True | True |

## Speedup

- GPU mean-latency speedup over CPU: `2.92x`
- GPU p95-latency speedup over CPU: `3.04x`

## Interpretation

The GPU path is substantially faster than the CPU path on this 100-frame YOLOv8n inference benchmark. Both CPU and GPU meet 30 Hz and 60 Hz latency budgets for this measured detector-only workload, with the GPU providing a larger latency margin.

## Claim boundary

This benchmark measures detector inference latency on preloaded KITTI frames. It does not include full robot system latency, camera transport, ROS 2 message passing, planner latency, or actuation. Those system-level costs are handled separately by the ROS 2 wrapper and diagnostic latency reports.

## Reproduction

Run:

    cd ~/projects/real-time-tracking-latency-budget
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate tracking-latency

    python scripts/benchmark_cpu_gpu_latency.py \
      --config configs/detector/yolov8n.yaml \
      --max-frames 100 \
      --warmup-frames 5 \
      --raw-output results/tables/m36_cpu_gpu_latency_raw.csv \
      --summary-output results/tables/m36_cpu_gpu_latency_summary.csv \
      --plot-output results/plots/m36_cpu_gpu_latency_comparison.png

## Raw sample

The raw file contains `200` rows: `100` CPU frames and `100` GPU frames.

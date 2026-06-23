# Environment

This project uses a small curated environment for the benchmark code and tests.

## Recommended setup

```bash
conda create -n tracking-latency python=3.11 -y
conda activate tracking-latency
python -m pip install -r environment/requirements-dev.txt
```

## Files

- `requirements-minimal.txt`: minimal runtime dependencies for detector/tracker/evaluation scripts.
- `requirements-dev.txt`: minimal dependencies plus test tooling.
- `requirements.txt`: alias of the minimal runtime requirements for common `pip install -r` usage.
- `environment.yml`: conda environment file with Python 3.11 and benchmark dependencies.
- `environment-lock-full.txt`: archived full local freeze for reference only.

The full lock file is intentionally not the recommended install path because it includes machine-specific ROS/Gazebo packages unrelated to this tracking benchmark.

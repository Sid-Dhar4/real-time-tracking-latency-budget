#!/usr/bin/env bash
set -euo pipefail

# Disable external pytest plugin autoload so ROS 2 system pytest plugins do not leak into this Conda environment.
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

python -m pytest -q tests/test_result_schema.py tests/test_kitti_format.py

#!/usr/bin/env bash
set -euo pipefail

# Disable external pytest plugins from ROS/other system installs so tests stay repo-local.
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

python -m pytest -q tests

# Environment

Primary environment for the MVP:

- Conda environment name: tracking-latency
- Python: 3.11
- Detector smoke test currently uses CPU because NVIDIA driver is not working through nvidia-smi.

Create:

conda create -n tracking-latency python=3.11 -y
conda activate tracking-latency

Install:

python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install ultralytics opencv-python pandas matplotlib pyyaml tqdm pytest

Freeze:

python -m pip freeze > environment/requirements.txt

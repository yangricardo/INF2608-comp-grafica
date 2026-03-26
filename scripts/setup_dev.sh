#!/usr/bin/env bash
set -euo pipefail

# Development setup script: creates venv, installs requirements and the package
# Usage: ./scripts/setup_dev.sh

PY=python3
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python
fi

echo "Using interpreter: $(command -v $PY)"

$PY -m venv .venv
echo "Created virtual environment .venv"

# Activate for the remainder of this script so pip installs go to the venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo
echo "Dev setup complete." 
echo "To start using the environment run:"
echo "  source .venv/bin/activate"
echo "Recommended ways to run the project after activating the venv:"
echo "  python -m src.ray_tracing_1       # runs package __main__"
echo "  python -m src.ray_tracing_1.main  # runs main.render() explicitly"

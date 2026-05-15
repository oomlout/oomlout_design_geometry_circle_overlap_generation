#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="python3"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

read -r -p "Word to preview in 3D: " WORD
if [[ -z "$WORD" ]]; then
  echo
  echo "3D preview failed. A word is required."
  exit 1
fi

echo
echo "Opening cinematic 3D preview..."
"$PYTHON_BIN" preview_3d.py --word "$WORD" --material topo_clay
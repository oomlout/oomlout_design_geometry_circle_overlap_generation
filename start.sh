#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="python3"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

read -r -p "Word to generate: " WORD
if [[ -z "$WORD" ]]; then
  echo
  echo "Start failed. A word is required."
  exit 1
fi

echo
echo "Generating 2D artwork and scene data..."
"$PYTHON_BIN" main.py --word "$WORD"
echo
echo "Generating 3D previews and orbit renders..."
"$PYTHON_BIN" preview_3d.py --word "$WORD" --all-materials
echo
echo "Refreshing gallery navigation..."
"$PYTHON_BIN" generate_navigation.py

echo
echo "Output gallery refreshed at output/README.md"
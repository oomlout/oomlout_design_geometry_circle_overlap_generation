from pathlib import Path

import pytest

from config import load_app_config


ROOT = Path(__file__).resolve().parents[1]


def test_load_app_config_reads_external_files() -> None:
    config = load_app_config(ROOT / "configuration" / "runtime.yaml")

    assert config.input_text == "joy"
    assert config.geometry.diameter == 52
    assert config.palette_name == "rainbow_dark"
    assert config.palette[0] == (153, 27, 27)


def test_load_app_config_rejects_unsupported_letters(tmp_path: Path) -> None:
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        f"""
input:
  text: joyz
data_files:
  encoding: {ROOT / 'configuration' / 'alphabets.yaml'}
  geometry: {ROOT / 'configuration' / 'geometry.yaml'}
  palettes: {ROOT / 'configuration' / 'palettes.yaml'}
canvas:
  width: 100
  height: 100
  border_width: 1
  background: [255, 255, 255]
palette:
  name: rainbow_dark
render:
  draw_circle_outlines: true
outputs:
  directory: ./output
  final_filename: working.png
  save_metadata: true
  sequence:
    enabled: false
    prefix: working_
  levels:
    enabled: false
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported characters"):
        load_app_config(config_path)
from pathlib import Path

import json
import yaml
import pytest

from main import get_preview_output, open_generated_image, prompt_for_word, run_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_run_from_config_writes_expected_outputs(tmp_path: Path) -> None:
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        f"""
input:
  text: a
data_files:
  encoding: {ROOT / 'configuration' / 'alphabets.yaml'}
  geometry: {ROOT / 'configuration' / 'geometry.yaml'}
  palettes: {ROOT / 'configuration' / 'palettes.yaml'}
canvas:
  width: 800
  height: 800
  border_width: 1
  background: [255, 255, 255]
palette:
  name: rainbow_dark
render:
  draw_circle_outlines: true
outputs:
  directory: ./generated
  final_filename: final.png
  save_metadata: true
  sequence:
    enabled: true
    prefix: frame_
  levels:
    enabled: true
  animation:
    enabled: true
    filename: final.gif
    duration_ms: 120
""".strip(),
        encoding="utf-8",
    )

    result = run_from_config(config_path)

    assert result.output_directory.name == "a"
    assert result.final_image.exists()
    assert result.animation is not None
    assert result.animation.exists()
    assert result.scene_3d is not None
    assert result.scene_3d.exists()
    assert (result.output_directory / "frame_0.png").exists()
    assert (result.output_directory / "frame_1.png").exists()
    assert (result.output_directory / "final" / "level_1.png").exists()
    assert (result.output_directory / "circles.yaml").exists()
    assert (result.output_directory / "effective_config.yaml").exists()

    circles = yaml.safe_load((result.output_directory / "circles.yaml").read_text(encoding="utf-8"))
    assert len(circles) == 2
    scene = json.loads((result.output_directory / "scene_3d.json").read_text(encoding="utf-8"))
    assert scene["scene_type"] == "layered_discs"
    assert len(scene["discs"]) == 2


def test_run_from_config_accepts_input_override(tmp_path: Path) -> None:
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        f"""
input:
  text: joy
data_files:
  encoding: {ROOT / 'configuration' / 'alphabets.yaml'}
  geometry: {ROOT / 'configuration' / 'geometry.yaml'}
  palettes: {ROOT / 'configuration' / 'palettes.yaml'}
canvas:
  width: 800
  height: 800
  border_width: 1
  background: [255, 255, 255]
palette:
  name: rainbow_dark
render:
  draw_circle_outlines: true
outputs:
  directory: ./generated
  final_filename: final.png
  save_metadata: true
  sequence:
    enabled: false
    prefix: frame_
  levels:
    enabled: false
  animation:
    enabled: false
    filename: final.gif
    duration_ms: 120
""".strip(),
        encoding="utf-8",
    )

    result = run_from_config(config_path, input_text_override="a")

    assert result.output_directory.name == "a"
    circles = yaml.safe_load((result.output_directory / "circles.yaml").read_text(encoding="utf-8"))
    assert len(circles) == 2


def test_prompt_for_word_returns_trimmed_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "  joy  ")

    assert prompt_for_word() == "joy"


def test_open_generated_image_uses_browser(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url: captured.append(url) or True)

    image_path = tmp_path / "working.png"
    image_path.write_bytes(b"test")
    open_generated_image(image_path)

    assert captured == [image_path.resolve().as_uri()]


def test_get_preview_output_prefers_animation(tmp_path: Path) -> None:
  final_image = tmp_path / "working.png"
  animation = tmp_path / "working.gif"

  result = run_from_config.__annotations__  # keep import usage simple in this file
  assert result is not None

  from main import RunResult

  preview_result = RunResult(
    config_path=tmp_path / "runtime.yaml",
    output_directory=tmp_path,
    circles=[],
    final_image=final_image,
    animation=animation,
    scene_3d=None,
  )
  assert get_preview_output(preview_result) == animation

  still_result = RunResult(
    config_path=tmp_path / "runtime.yaml",
    output_directory=tmp_path,
    circles=[],
    final_image=final_image,
    animation=None,
    scene_3d=None,
  )
  assert get_preview_output(still_result) == final_image
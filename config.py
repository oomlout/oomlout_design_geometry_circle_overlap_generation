from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class EncodingConfig:
    braille: dict[str, list[list[bool]]]
    morse: dict[str, list[str]]


@dataclass(frozen=True)
class GeometryConfig:
    grid_width: int
    grid_height: int
    diameter: float
    spacing: int
    spacing_letter: int
    start_shift_x: int
    start_shift_y: int
    initial_dash_multiplier: float
    next_dot_multiplier: float
    next_dash_multiplier: float


@dataclass(frozen=True)
class CanvasConfig:
    width: int
    height: int
    border_width: int
    background: tuple[int, int, int]


@dataclass(frozen=True)
class OutputConfig:
    directory: Path
    final_filename: str
    save_metadata: bool
    sequence_enabled: bool
    sequence_prefix: str
    levels_enabled: bool
    animation_enabled: bool
    animation_filename: str
    animation_duration_ms: int


@dataclass(frozen=True)
class RenderConfig:
    draw_circle_outlines: bool


@dataclass(frozen=True)
class AppConfig:
    source_path: Path
    input_text: str
    encoding: EncodingConfig
    geometry: GeometryConfig
    canvas: CanvasConfig
    palette_name: str
    palette: list[tuple[int, int, int]]
    outputs: OutputConfig
    render: RenderConfig


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return data


def _resolve_relative_path(base_path: Path, configured_path: str) -> Path:
    candidate = Path(configured_path)
    if not candidate.is_absolute():
        candidate = (base_path.parent / candidate).resolve()
    return candidate


def _validate_rgb_triplet(name: str, value: list[int] | tuple[int, int, int]) -> tuple[int, int, int]:
    if len(value) != 3:
        raise ValueError(f"{name} must contain exactly three integers")
    triplet = tuple(int(component) for component in value)
    if any(component < 0 or component > 255 for component in triplet):
        raise ValueError(f"{name} values must be within 0-255")
    return triplet


def _load_encoding(path: Path) -> EncodingConfig:
    data = _load_yaml(path)
    braille = data.get("braille", {})
    morse = data.get("morse", {})
    if not isinstance(braille, dict) or not isinstance(morse, dict):
        raise ValueError("Encoding file must contain braille and morse mappings")
    return EncodingConfig(braille=braille, morse=morse)


def _load_geometry(path: Path) -> GeometryConfig:
    data = _load_yaml(path)
    letter_grid = data.get("letter_grid", {})
    return GeometryConfig(
        grid_width=int(letter_grid.get("width", 0)),
        grid_height=int(letter_grid.get("height", 0)),
        diameter=float(data.get("diameter", 0)),
        spacing=int(data.get("spacing", 0)),
        spacing_letter=int(data.get("spacing_letter", 0)),
        start_shift_x=int(data.get("start_shift_x", 0)),
        start_shift_y=int(data.get("start_shift_y", 0)),
        initial_dash_multiplier=float(data.get("initial_dash_multiplier", 0)),
        next_dot_multiplier=float(data.get("next_dot_multiplier", 0)),
        next_dash_multiplier=float(data.get("next_dash_multiplier", 0)),
    )


def _load_palette(path: Path, palette_name: str) -> list[tuple[int, int, int]]:
    data = _load_yaml(path)
    palettes = data.get("palettes", {})
    if palette_name not in palettes:
        raise ValueError(f"Palette '{palette_name}' was not found in {path}")
    colors = palettes[palette_name]
    if not isinstance(colors, list) or not colors:
        raise ValueError(f"Palette '{palette_name}' must contain at least one color")
    return [_validate_rgb_triplet(f"palette {palette_name}", color) for color in colors]


def _validate_geometry(geometry: GeometryConfig) -> None:
    if geometry.grid_width <= 0 or geometry.grid_height <= 0:
        raise ValueError("Geometry grid dimensions must be positive")
    if geometry.diameter <= 0:
        raise ValueError("Geometry diameter must be positive")
    if geometry.spacing <= 0 or geometry.spacing_letter <= 0:
        raise ValueError("Geometry spacing values must be positive")
    if geometry.initial_dash_multiplier <= 0:
        raise ValueError("Geometry initial_dash_multiplier must be positive")
    if geometry.next_dot_multiplier <= 0 or geometry.next_dash_multiplier <= 0:
        raise ValueError("Geometry multipliers must be positive")


def _validate_encoding(encoding: EncodingConfig, geometry: GeometryConfig) -> None:
    for letter, pattern in encoding.braille.items():
        if len(pattern) != geometry.grid_height:
            raise ValueError(f"Braille pattern for '{letter}' has the wrong height")
        for row in pattern:
            if len(row) != geometry.grid_width:
                raise ValueError(f"Braille pattern for '{letter}' has the wrong width")
    for letter, symbols in encoding.morse.items():
        if not symbols:
            raise ValueError(f"Morse pattern for '{letter}' must not be empty")
        if any(symbol not in {"dot", "dash"} for symbol in symbols):
            raise ValueError(f"Morse pattern for '{letter}' contains an unknown symbol")


def _validate_text(input_text: str, encoding: EncodingConfig) -> None:
    unsupported = sorted(
        {
            character
            for character in input_text
            if character != " " and (character not in encoding.braille or character not in encoding.morse)
        }
    )
    if unsupported:
        unsupported_text = ", ".join(unsupported)
        raise ValueError(f"Input text contains unsupported characters: {unsupported_text}")


def load_app_config(
    config_path: str | Path,
    output_directory: str | Path | None = None,
    input_text_override: str | None = None,
) -> AppConfig:
    config_path = Path(config_path).resolve()
    root_data = _load_yaml(config_path)

    input_text = input_text_override if input_text_override is not None else root_data.get("input", {}).get("text", "")
    input_text = str(input_text).strip().lower()
    if not input_text:
        raise ValueError("input.text must not be empty")

    encoding_path = _resolve_relative_path(config_path, root_data["data_files"]["encoding"])
    geometry_path = _resolve_relative_path(config_path, root_data["data_files"]["geometry"])
    palette_path = _resolve_relative_path(config_path, root_data["data_files"]["palettes"])

    encoding = _load_encoding(encoding_path)
    geometry = _load_geometry(geometry_path)
    _validate_geometry(geometry)
    _validate_encoding(encoding, geometry)
    _validate_text(input_text, encoding)

    canvas_data = root_data.get("canvas", {})
    canvas = CanvasConfig(
        width=int(canvas_data.get("width", 0)),
        height=int(canvas_data.get("height", 0)),
        border_width=int(canvas_data.get("border_width", 1)),
        background=_validate_rgb_triplet("canvas.background", canvas_data.get("background", [255, 255, 255])),
    )
    if canvas.width <= 0 or canvas.height <= 0:
        raise ValueError("Canvas width and height must be positive")

    palette_name = str(root_data.get("palette", {}).get("name", ""))
    if not palette_name:
        raise ValueError("palette.name must not be empty")
    palette = _load_palette(palette_path, palette_name)

    outputs_data = root_data.get("outputs", {})
    if output_directory is None:
        output_directory = outputs_data.get("directory", "output")
    output_path = _resolve_relative_path(config_path, str(output_directory))
    output_config = OutputConfig(
        directory=output_path,
        final_filename=str(outputs_data.get("final_filename", "working.png")),
        save_metadata=bool(outputs_data.get("save_metadata", True)),
        sequence_enabled=bool(outputs_data.get("sequence", {}).get("enabled", False)),
        sequence_prefix=str(outputs_data.get("sequence", {}).get("prefix", "working_")),
        levels_enabled=bool(outputs_data.get("levels", {}).get("enabled", False)),
        animation_enabled=bool(outputs_data.get("animation", {}).get("enabled", False)),
        animation_filename=str(outputs_data.get("animation", {}).get("filename", "working.gif")),
        animation_duration_ms=int(outputs_data.get("animation", {}).get("duration_ms", 250)),
    )

    render_config = RenderConfig(draw_circle_outlines=bool(root_data.get("render", {}).get("draw_circle_outlines", True)))

    return AppConfig(
        source_path=config_path,
        input_text=input_text,
        encoding=encoding,
        geometry=geometry,
        canvas=canvas,
        palette_name=palette_name,
        palette=palette,
        outputs=output_config,
        render=render_config,
    )
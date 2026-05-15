from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import webbrowser

import yaml

from config import AppConfig, load_app_config
from generator import generate_text_circles, generate_text_scene
from rendering import create_animation, render_artwork
from scene3d import serialize_scene


@dataclass(frozen=True)
class RunResult:
    config_path: Path
    output_directory: Path
    circles: list[tuple[float, float, float]]
    final_image: Path
    animation: Path | None
    scene_3d: Path | None


def _serialize_config(config: AppConfig) -> dict:
    data = asdict(config)
    data["source_path"] = str(config.source_path)
    data["outputs"]["directory"] = str(config.outputs.directory)
    return data


def _serialize_circles(circles: list[tuple[float, float, float]]) -> list[dict[str, float]]:
    return [
        {"x": center_x, "y": center_y, "radius": radius}
        for center_x, center_y, radius in circles
    ]


def prompt_for_word() -> str:
    word = input("Word to generate: ").strip()
    if not word:
        raise ValueError("A word is required.")
    return word


def open_generated_image(image_path: Path) -> None:
    webbrowser.open(image_path.resolve().as_uri())


def get_preview_output(result: RunResult) -> Path:
    return result.animation if result.animation is not None else result.final_image


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the 2D artwork and metadata for a word.")
    parser.add_argument("--word", help="Optional word override to generate without prompting.")
    parser.add_argument("--no-open", action="store_true", help="Do not open the generated 2D preview in a browser.")
    return parser


def run_from_config(
    config_path: str | Path,
    output_directory: str | Path | None = None,
    input_text_override: str | None = None,
) -> RunResult:
    config = load_app_config(
        config_path,
        output_directory=output_directory,
        input_text_override=input_text_override,
    )
    scene_3d = generate_text_scene(
        input_text=config.input_text,
        encoding=config.encoding,
        geometry=config.geometry,
        canvas_width=config.canvas.width,
        canvas_height=config.canvas.height,
        palette=config.palette,
    )
    circles = [(disc.x, disc.y, disc.radius) for disc in scene_3d.discs]

    final_output = config.outputs.directory / config.outputs.final_filename
    animation_output: Path | None = None
    scene_3d_output: Path | None = None
    frame_paths: list[Path] = []

    if config.outputs.sequence_enabled:
        for index in range(len(circles)):
            sequence_output = config.outputs.directory / f"{config.outputs.sequence_prefix}{index}.png"
            frame_paths.append(sequence_output)
            render_artwork(
                width=config.canvas.width,
                height=config.canvas.height,
                circles=circles[: index + 1],
                colors=config.palette,
                background=config.canvas.background,
                border_width=config.canvas.border_width,
                draw_circle_outlines=config.render.draw_circle_outlines,
                file_output=sequence_output,
                save_levels=False,
            )

    if config.outputs.animation_enabled:
        if not frame_paths:
            for index in range(len(circles)):
                sequence_output = config.outputs.directory / f"{config.outputs.sequence_prefix}{index}.png"
                frame_paths.append(sequence_output)
                render_artwork(
                    width=config.canvas.width,
                    height=config.canvas.height,
                    circles=circles[: index + 1],
                    colors=config.palette,
                    background=config.canvas.background,
                    border_width=config.canvas.border_width,
                    draw_circle_outlines=config.render.draw_circle_outlines,
                    file_output=sequence_output,
                    save_levels=False,
                )
        animation_output = create_animation(
            frame_paths=frame_paths,
            animation_output=config.outputs.directory / config.outputs.animation_filename,
            duration_ms=config.outputs.animation_duration_ms,
        )

    render_artwork(
        width=config.canvas.width,
        height=config.canvas.height,
        circles=circles,
        colors=config.palette,
        background=config.canvas.background,
        border_width=config.canvas.border_width,
        draw_circle_outlines=config.render.draw_circle_outlines,
        file_output=final_output,
        save_levels=config.outputs.levels_enabled,
    )

    if config.outputs.save_metadata:
        config.outputs.directory.mkdir(parents=True, exist_ok=True)
        with (config.outputs.directory / "circles.yaml").open("w", encoding="utf-8") as circles_file:
            yaml.safe_dump(_serialize_circles(circles), circles_file, sort_keys=False)
        with (config.outputs.directory / "effective_config.yaml").open("w", encoding="utf-8") as config_file:
            yaml.safe_dump(_serialize_config(config), config_file, sort_keys=False)
        scene_3d_output = config.outputs.directory / "scene_3d.json"
        with scene_3d_output.open("w", encoding="utf-8") as scene_file:
            json.dump(serialize_scene(scene_3d), scene_file, indent=2)

    return RunResult(
        config_path=config.source_path,
        output_directory=config.outputs.directory,
        circles=circles,
        final_image=final_output,
        animation=animation_output,
        scene_3d=scene_3d_output,
    )


if __name__ == "__main__":
    args = build_argument_parser().parse_args()
    input_word = args.word if args.word is not None else prompt_for_word()
    print(f"Generating 2D artwork and scene data for '{input_word}'...")
    result = run_from_config(
        Path("configuration") / "runtime.yaml",
        input_text_override=input_word,
    )
    print(f"Generated image: {result.final_image}")
    if result.animation is not None:
        print(f"Generated 2D animation: {result.animation}")
    if result.scene_3d is not None:
        print(f"Generated 3D scene: {result.scene_3d}")
    if not args.no_open:
        open_generated_image(get_preview_output(result))
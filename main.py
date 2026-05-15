from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import webbrowser

import yaml

from config import AppConfig, load_app_config
from generator import generate_text_circles
from rendering import create_animation, render_artwork


@dataclass(frozen=True)
class RunResult:
    config_path: Path
    output_directory: Path
    circles: list[tuple[float, float, float]]
    final_image: Path
    animation: Path | None


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
    circles = generate_text_circles(
        input_text=config.input_text,
        encoding=config.encoding,
        geometry=config.geometry,
    )

    final_output = config.outputs.directory / config.outputs.final_filename
    animation_output: Path | None = None
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

    return RunResult(
        config_path=config.source_path,
        output_directory=config.outputs.directory,
        circles=circles,
        final_image=final_output,
        animation=animation_output,
    )


if __name__ == "__main__":
    result = run_from_config(
        Path("configuration") / "runtime.yaml",
        input_text_override=prompt_for_word(),
    )
    open_generated_image(get_preview_output(result))
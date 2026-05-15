from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


Circle = tuple[float, float, float]


def build_overlap_matrix(width: int, height: int, circles: list[Circle]) -> np.ndarray:
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    overlap_matrix = np.zeros((height, width), dtype=int)

    for center_x, center_y, radius in circles:
        mask = (x_coords - center_x) ** 2 + (y_coords - center_y) ** 2 <= radius ** 2
        overlap_matrix += mask

    return overlap_matrix


def render_image(
    overlap_matrix: np.ndarray,
    colors: list[tuple[int, int, int]],
    background: tuple[int, int, int],
    circles: list[Circle],
    border_width: int,
    draw_circle_outlines: bool,
) -> Image.Image:
    image_data = np.empty((overlap_matrix.shape[0], overlap_matrix.shape[1], 3), dtype=np.uint8)
    image_data[:] = background

    for count in np.unique(overlap_matrix):
        if count <= 0:
            continue
        image_data[overlap_matrix == count] = colors[count % len(colors)]

    image = Image.fromarray(image_data, "RGB")

    if draw_circle_outlines:
        draw = ImageDraw.Draw(image)
        for center_x, center_y, radius in circles:
            draw.ellipse(
                (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
                outline=(0, 0, 0),
                width=border_width,
            )

    return image


def save_level_masks(overlap_matrix: np.ndarray, background: tuple[int, int, int], output_directory: Path, stem: str) -> None:
    level_directory = output_directory / stem
    level_directory.mkdir(parents=True, exist_ok=True)
    for stale_file in level_directory.glob("level_*.png"):
        stale_file.unlink()
    max_level = int(np.max(overlap_matrix))

    for level in range(1, max_level + 1):
        image_data = np.empty((overlap_matrix.shape[0], overlap_matrix.shape[1], 3), dtype=np.uint8)
        image_data[:] = background
        image_data[overlap_matrix >= level] = (0, 0, 0)
        Image.fromarray(image_data, "RGB").save(level_directory / f"level_{level}.png")


def render_artwork(
    width: int,
    height: int,
    circles: list[Circle],
    colors: list[tuple[int, int, int]],
    background: tuple[int, int, int],
    border_width: int,
    draw_circle_outlines: bool,
    file_output: Path,
    save_levels: bool,
) -> np.ndarray:
    file_output.parent.mkdir(parents=True, exist_ok=True)
    overlap_matrix = build_overlap_matrix(width=width, height=height, circles=circles)
    image = render_image(
        overlap_matrix=overlap_matrix,
        colors=colors,
        background=background,
        circles=circles,
        border_width=border_width,
        draw_circle_outlines=draw_circle_outlines,
    )
    image.save(file_output)

    if save_levels:
        save_level_masks(overlap_matrix=overlap_matrix, background=background, output_directory=file_output.parent, stem=file_output.stem)

    return overlap_matrix


def create_animation(
    frame_paths: list[Path],
    animation_output: Path,
    duration_ms: int,
) -> Path:
    if not frame_paths:
        raise ValueError("At least one frame is required to create an animation")

    animation_output.parent.mkdir(parents=True, exist_ok=True)
    frames: list[Image.Image] = []

    for frame_path in frame_paths:
        with Image.open(frame_path) as image:
            frames.append(image.convert("P", palette=Image.Palette.ADAPTIVE))

    frames[0].save(
        animation_output,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
    )
    return animation_output
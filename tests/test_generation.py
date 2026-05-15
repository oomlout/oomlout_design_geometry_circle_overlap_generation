from pathlib import Path

from config import load_app_config
from generator import generate_text_circles, generate_text_scene


ROOT = Path(__file__).resolve().parents[1]

def _bounds(circles: list[tuple[float, float, float]]) -> tuple[float, float, float, float]:
    return (
        min(center_x - radius for center_x, _, radius in circles),
        max(center_x + radius for center_x, _, radius in circles),
        min(center_y - radius for _, center_y, radius in circles),
        max(center_y + radius for _, center_y, radius in circles),
    )


def test_generate_text_circles_centers_joy_on_canvas() -> None:
    config = load_app_config(ROOT / "configuration" / "runtime.yaml")

    circles = generate_text_circles(
        input_text=config.input_text,
        encoding=config.encoding,
        geometry=config.geometry,
        canvas_width=config.canvas.width,
        canvas_height=config.canvas.height,
        palette=config.palette,
    )

    min_x, max_x, min_y, max_y = _bounds(circles)

    assert len(circles) == 41
    assert ((min_x + max_x) / 2) == config.canvas.width / 2
    assert ((min_y + max_y) / 2) == config.canvas.height / 2


def test_generate_text_circles_repositions_longer_words_to_stay_centered() -> None:
    config = load_app_config(ROOT / "configuration" / "runtime.yaml")

    short_circles = generate_text_circles(
        input_text="a",
        encoding=config.encoding,
        geometry=config.geometry,
        canvas_width=config.canvas.width,
        canvas_height=config.canvas.height,
        palette=config.palette,
    )
    long_circles = generate_text_circles(
        input_text="joy",
        encoding=config.encoding,
        geometry=config.geometry,
        canvas_width=config.canvas.width,
        canvas_height=config.canvas.height,
        palette=config.palette,
    )

    short_min_x, short_max_x, _, _ = _bounds(short_circles)
    long_min_x, long_max_x, _, _ = _bounds(long_circles)

    assert short_min_x > long_min_x
    assert ((short_min_x + short_max_x) / 2) == config.canvas.width / 2
    assert ((long_min_x + long_max_x) / 2) == config.canvas.width / 2


def test_generate_text_scene_contains_3d_disc_metadata() -> None:
    config = load_app_config(ROOT / "configuration" / "runtime.yaml")

    scene = generate_text_scene(
        input_text="a",
        encoding=config.encoding,
        geometry=config.geometry,
        canvas_width=config.canvas.width,
        canvas_height=config.canvas.height,
        palette=config.palette,
    )

    assert scene.schema_version == "1.0"
    assert scene.scene_type == "layered_discs"
    assert len(scene.discs) == 2
    assert scene.discs[0].character == "a"
    assert scene.discs[0].morse_index == 0
    assert scene.discs[1].z == scene.discs[1].thickness / 2
    assert scene.discs[0].z > scene.discs[1].z
    assert scene.discs[0].z - scene.discs[1].z == scene.discs[0].thickness
    assert scene.discs[1].radius > scene.discs[0].radius
    assert scene.spacing["z"] == scene.discs[0].thickness
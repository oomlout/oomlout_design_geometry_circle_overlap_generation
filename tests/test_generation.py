from pathlib import Path

from config import load_app_config
from generator import generate_text_circles


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
    )
    long_circles = generate_text_circles(
        input_text="joy",
        encoding=config.encoding,
        geometry=config.geometry,
        canvas_width=config.canvas.width,
        canvas_height=config.canvas.height,
    )

    short_min_x, short_max_x, _, _ = _bounds(short_circles)
    long_min_x, long_max_x, _, _ = _bounds(long_circles)

    assert short_min_x > long_min_x
    assert ((short_min_x + short_max_x) / 2) == config.canvas.width / 2
    assert ((long_min_x + long_max_x) / 2) == config.canvas.width / 2
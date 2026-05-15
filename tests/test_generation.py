from pathlib import Path

from config import load_app_config
from generator import generate_text_circles


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_JOY_CIRCLES = [
    (500, 600, 26.0),
    (500, 600, 52.0),
    (500, 600, 104.0),
    (500, 600, 208.0),
    (600, 500, 26.0),
    (600, 500, 52.0),
    (600, 500, 104.0),
    (600, 500, 208.0),
    (600, 600, 26.0),
    (600, 600, 52.0),
    (600, 600, 104.0),
    (600, 600, 208.0),
    (740, 500, 41.6),
    (740, 500, 83.2),
    (740, 500, 166.4),
    (740, 700, 41.6),
    (740, 700, 83.2),
    (740, 700, 166.4),
    (840, 600, 41.6),
    (840, 600, 83.2),
    (840, 600, 166.4),
    (980, 500, 41.6),
    (980, 500, 52.0),
    (980, 500, 104.0),
    (980, 500, 208.0),
    (980, 700, 41.6),
    (980, 700, 52.0),
    (980, 700, 104.0),
    (980, 700, 208.0),
    (1080, 500, 41.6),
    (1080, 500, 52.0),
    (1080, 500, 104.0),
    (1080, 500, 208.0),
    (1080, 600, 41.6),
    (1080, 600, 52.0),
    (1080, 600, 104.0),
    (1080, 600, 208.0),
    (1080, 700, 41.6),
    (1080, 700, 52.0),
    (1080, 700, 104.0),
    (1080, 700, 208.0),
]


def test_generate_text_circles_matches_old_joy_baseline() -> None:
    config = load_app_config(ROOT / "configuration" / "runtime.yaml")

    circles = generate_text_circles(
        input_text=config.input_text,
        encoding=config.encoding,
        geometry=config.geometry,
    )

    assert circles == EXPECTED_JOY_CIRCLES
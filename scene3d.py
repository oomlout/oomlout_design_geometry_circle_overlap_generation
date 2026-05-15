from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SceneDisc:
    circle_index: int
    letter_index: int
    character: str
    braille_cell_x: int
    braille_cell_y: int
    morse_index: int
    x: float
    y: float
    z: float
    radius: float
    thickness: float
    color: tuple[int, int, int]
    opacity: float
    material_key: str


@dataclass(frozen=True)
class Scene3D:
    schema_version: str
    scene_type: str
    input_text: str
    canvas: dict[str, float]
    spacing: dict[str, float]
    discs: list[SceneDisc]


def serialize_scene(scene: Scene3D) -> dict:
    data = asdict(scene)
    for disc in data["discs"]:
        disc["color"] = list(disc["color"])
    return data
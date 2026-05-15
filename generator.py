from __future__ import annotations

from config import EncodingConfig, GeometryConfig
from scene3d import Scene3D, SceneDisc


Circle = tuple[float, float, float]


def _material_opacity(morse_index: int) -> float:
    return min(0.3 + (morse_index * 0.12), 0.9)


def _disc_thickness(geometry: GeometryConfig) -> float:
    return max(geometry.diameter * 0.18, 1.0)


def _generate_raw_text_scene_discs(
    input_text: str,
    encoding: EncodingConfig,
    geometry: GeometryConfig,
    palette: list[tuple[int, int, int]],
) -> list[SceneDisc]:
    discs: list[SceneDisc] = []
    current_x = geometry.start_shift_x
    current_y = geometry.start_shift_y
    thickness = _disc_thickness(geometry)
    z_step = thickness

    for letter_index, letter in enumerate(input_text):
        if letter == " ":
            current_x += geometry.spacing_letter
            continue

        braille_pattern = encoding.braille[letter]
        morse_pattern = encoding.morse[letter]

        for x_index in range(geometry.grid_width):
            for y_index in range(geometry.grid_height):
                if not braille_pattern[y_index][x_index]:
                    continue

                current_diameter = geometry.diameter
                if morse_pattern[0] == "dash":
                    current_diameter *= geometry.initial_dash_multiplier

                dot_x = current_x + (x_index * geometry.spacing)
                dot_y = current_y + (y_index * geometry.spacing)
                morse_discs: list[dict[str, float | int]] = []

                for index, _ in enumerate(morse_pattern):
                    morse_discs.append(
                        {
                            "morse_index": index,
                            "radius": current_diameter / 2,
                            "opacity": _material_opacity(index),
                        }
                    )
                    if index == len(morse_pattern) - 1:
                        continue
                    next_symbol = morse_pattern[index + 1]
                    if next_symbol == "dot":
                        current_diameter = geometry.diameter * geometry.next_dot_multiplier
                    else:
                        current_diameter *= geometry.next_dash_multiplier

                stack_level_by_index = {
                    int(disc["morse_index"]): level
                    for level, disc in enumerate(
                        sorted(
                            morse_discs,
                            key=lambda disc: (-float(disc["radius"]), int(disc["morse_index"])),
                        )
                    )
                }

                for disc_data in morse_discs:
                    morse_index = int(disc_data["morse_index"])
                    radius = float(disc_data["radius"])
                    opacity = float(disc_data["opacity"])
                    stack_level = stack_level_by_index[morse_index]
                    discs.append(
                        SceneDisc(
                            circle_index=len(discs),
                            letter_index=letter_index,
                            character=letter,
                            braille_cell_x=x_index,
                            braille_cell_y=y_index,
                            morse_index=morse_index,
                            x=dot_x,
                            y=dot_y,
                            z=(stack_level * z_step) + (thickness / 2),
                            radius=radius,
                            thickness=thickness,
                            color=palette[letter_index % len(palette)],
                            opacity=opacity,
                            material_key=f"letter_{letter_index % len(palette)}",
                        )
                    )

        current_x += geometry.spacing_letter

    return discs


def _center_scene_discs(discs: list[SceneDisc], canvas_width: int, canvas_height: int) -> list[SceneDisc]:
    if not discs:
        return []

    min_x = min(disc.x - disc.radius for disc in discs)
    max_x = max(disc.x + disc.radius for disc in discs)
    min_y = min(disc.y - disc.radius for disc in discs)
    max_y = max(disc.y + disc.radius for disc in discs)

    shift_x = (canvas_width / 2) - ((min_x + max_x) / 2)
    shift_y = (canvas_height / 2) - ((min_y + max_y) / 2)

    return [
        SceneDisc(
            circle_index=disc.circle_index,
            letter_index=disc.letter_index,
            character=disc.character,
            braille_cell_x=disc.braille_cell_x,
            braille_cell_y=disc.braille_cell_y,
            morse_index=disc.morse_index,
            x=disc.x + shift_x,
            y=disc.y + shift_y,
            z=disc.z,
            radius=disc.radius,
            thickness=disc.thickness,
            color=disc.color,
            opacity=disc.opacity,
            material_key=disc.material_key,
        )
        for disc in discs
    ]


def generate_text_scene(
    input_text: str,
    encoding: EncodingConfig,
    geometry: GeometryConfig,
    canvas_width: int,
    canvas_height: int,
    palette: list[tuple[int, int, int]],
) -> Scene3D:
    discs = _generate_raw_text_scene_discs(
        input_text=input_text,
        encoding=encoding,
        geometry=geometry,
        palette=palette,
    )
    centered_discs = _center_scene_discs(discs, canvas_width=canvas_width, canvas_height=canvas_height)
    return Scene3D(
        schema_version="1.0",
        scene_type="layered_discs",
        input_text=input_text,
        canvas={"width": canvas_width, "height": canvas_height},
        spacing={
            "letter": geometry.spacing_letter,
            "grid": geometry.spacing,
            "z": _disc_thickness(geometry),
        },
        discs=centered_discs,
    )


def generate_text_circles(
    input_text: str,
    encoding: EncodingConfig,
    geometry: GeometryConfig,
    canvas_width: int,
    canvas_height: int,
    palette: list[tuple[int, int, int]] | None = None,
) -> list[Circle]:
    if palette is None:
        palette = [(255, 255, 255)]
    scene = generate_text_scene(
        input_text=input_text,
        encoding=encoding,
        geometry=geometry,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        palette=palette,
    )
    return [(disc.x, disc.y, disc.radius) for disc in scene.discs]
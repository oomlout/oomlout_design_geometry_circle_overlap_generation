from __future__ import annotations

from config import EncodingConfig, GeometryConfig


Circle = tuple[float, float, float]


def _generate_raw_text_circles(input_text: str, encoding: EncodingConfig, geometry: GeometryConfig) -> list[Circle]:
    circles: list[Circle] = []
    current_x = geometry.start_shift_x
    current_y = geometry.start_shift_y

    for letter in input_text:
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

                for index, _ in enumerate(morse_pattern):
                    circles.append((dot_x, dot_y, current_diameter / 2))
                    if index == len(morse_pattern) - 1:
                        continue
                    next_symbol = morse_pattern[index + 1]
                    if next_symbol == "dot":
                        current_diameter = geometry.diameter * geometry.next_dot_multiplier
                    else:
                        current_diameter *= geometry.next_dash_multiplier

        current_x += geometry.spacing_letter

    return circles


def _center_circles(circles: list[Circle], canvas_width: int, canvas_height: int) -> list[Circle]:
    if not circles:
        return []

    min_x = min(center_x - radius for center_x, _, radius in circles)
    max_x = max(center_x + radius for center_x, _, radius in circles)
    min_y = min(center_y - radius for _, center_y, radius in circles)
    max_y = max(center_y + radius for _, center_y, radius in circles)

    shift_x = (canvas_width / 2) - ((min_x + max_x) / 2)
    shift_y = (canvas_height / 2) - ((min_y + max_y) / 2)

    return [
        (center_x + shift_x, center_y + shift_y, radius)
        for center_x, center_y, radius in circles
    ]


def generate_text_circles(
    input_text: str,
    encoding: EncodingConfig,
    geometry: GeometryConfig,
    canvas_width: int,
    canvas_height: int,
) -> list[Circle]:
    circles = _generate_raw_text_circles(
        input_text=input_text,
        encoding=encoding,
        geometry=geometry,
    )
    return _center_circles(circles, canvas_width=canvas_width, canvas_height=canvas_height)
from __future__ import annotations

from config import EncodingConfig, GeometryConfig


Circle = tuple[float, float, float]


def generate_text_circles(input_text: str, encoding: EncodingConfig, geometry: GeometryConfig) -> list[Circle]:
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
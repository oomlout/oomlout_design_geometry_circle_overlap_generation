from pathlib import Path

from rendering import build_overlap_matrix, render_artwork


def test_build_overlap_matrix_counts_overlaps() -> None:
    circles = [(1, 1, 1), (2, 1, 1)]

    overlap_matrix = build_overlap_matrix(width=5, height=4, circles=circles)

    assert overlap_matrix[1, 1] == 2
    assert overlap_matrix[1, 2] == 2
    assert overlap_matrix[1, 0] == 1
    assert overlap_matrix[1, 3] == 1
    assert overlap_matrix[3, 4] == 0


def test_render_artwork_saves_image_and_levels(tmp_path: Path) -> None:
    circles = [(1, 1, 1), (2, 1, 1)]
    file_output = tmp_path / "render.png"

    render_artwork(
        width=5,
        height=4,
        circles=circles,
        colors=[(1, 1, 1), (10, 10, 10), (20, 20, 20)],
        background=(255, 255, 255),
        border_width=0,
        draw_circle_outlines=False,
        file_output=file_output,
        save_levels=True,
    )

    assert file_output.exists()
    assert (tmp_path / "render" / "level_1.png").exists()
    assert (tmp_path / "render" / "level_2.png").exists()
    assert not (tmp_path / "render" / "level_0.png").exists()
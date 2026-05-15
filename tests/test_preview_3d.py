import json
from pathlib import Path

import pytest

from preview_3d import (
    DEFAULT_MATERIAL,
    ORBIT_PATH_FACTOR,
    ORBIT_HEIGHT_SWING_RATIO,
    PREVIEW_CONTACT_OVERLAP,
    PREVIEW_DEPTH_SCALE,
    SHOWCASE_MATERIALS,
    PREVIEW_THICKNESS_SCALE,
    build_orbit_path,
    orbit_preview_output_name,
    load_scene,
    material_output_name,
    plot_coordinates,
    preview_bounds,
    preview_thickness,
    resolve_scene_from_args,
    resolve_material_style,
    scene_bounds,
    scene_paths_for_word,
    slugify_word,
)


def test_slugify_word_matches_output_folder_style() -> None:
    assert slugify_word("Aaron Joy") == "aaron_joy"


def test_scene_paths_for_word_points_to_scene_and_screenshot() -> None:
    paths = scene_paths_for_word("joy")

    assert paths.scene_path.name == "scene_3d.json"
    assert paths.scene_path.parent.name == "joy"
    assert paths.screenshot_path.name == "preview_3d.png"
    assert paths.orbit_preview_path.name == "preview_3d_orbit_preview.png"
    assert paths.orbit_path.name == "preview_3d_orbit.gif"


def test_material_output_name_keeps_default_and_suffixes_variants() -> None:
    assert material_output_name(DEFAULT_MATERIAL, "preview_3d", "png") == "preview_3d.png"
    assert material_output_name("satin_brass", "preview_3d", "png") == "preview_3d_satin_brass.png"


def test_orbit_preview_output_name_matches_material_suffix_style() -> None:
    assert orbit_preview_output_name(DEFAULT_MATERIAL) == "preview_3d_orbit_preview.png"
    assert orbit_preview_output_name("glow_coral") == "preview_3d_orbit_preview_glow_coral.png"


def test_showcase_materials_include_translucent_and_glow_styles() -> None:
    assert "translucent_glass" in SHOWCASE_MATERIALS
    assert "glow_coral" in SHOWCASE_MATERIALS


def test_resolve_material_style_rejects_unknown_material() -> None:
    with pytest.raises(ValueError, match="Unknown material"):
        resolve_material_style("unknown")


def test_load_scene_reads_json(tmp_path: Path) -> None:
    scene_path = tmp_path / "scene_3d.json"
    scene_path.write_text(json.dumps({"canvas": {"width": 10, "height": 20}, "discs": []}), encoding="utf-8")

    scene = load_scene(scene_path)

    assert scene["canvas"]["width"] == 10


def test_scene_bounds_and_plot_coordinates_are_consistent() -> None:
    scene = {
        "canvas": {"width": 1000, "height": 800},
        "discs": [
            {"x": 100.0, "y": 200.0, "z": 0.0, "radius": 20.0, "thickness": 10.0},
            {"x": 300.0, "y": 500.0, "z": 40.0, "radius": 50.0, "thickness": 12.0},
        ],
    }

    bounds = scene_bounds(scene)
    coords = plot_coordinates(scene["discs"][0], scene["canvas"])

    assert bounds["min_x"] == 80.0
    assert bounds["max_y"] == 550.0
    assert coords == (-400.0, 200.0, 0.0)


def test_preview_bounds_and_thickness_apply_depth_exaggeration() -> None:
    scene = {
        "canvas": {"width": 1000, "height": 800},
        "discs": [
            {"x": 500.0, "y": 400.0, "z": 10.0, "radius": 20.0, "thickness": 10.0},
            {"x": 600.0, "y": 420.0, "z": 20.0, "radius": 30.0, "thickness": 8.0},
        ],
    }

    bounds = preview_bounds(scene)

    assert plot_coordinates(scene["discs"][1], scene["canvas"]) == (100.0, -20.0, 20.0 * PREVIEW_DEPTH_SCALE)
    assert preview_thickness(scene["discs"][0]) == (10.0 * PREVIEW_THICKNESS_SCALE) + PREVIEW_CONTACT_OVERLAP
    touching_gap = plot_coordinates(scene["discs"][1], scene["canvas"])[2] - plot_coordinates(scene["discs"][0], scene["canvas"])[2]
    assert touching_gap == 10.0 * PREVIEW_DEPTH_SCALE
    assert preview_thickness(scene["discs"][0]) > touching_gap
    assert bounds["max_z"] > scene_bounds(scene)["max_z"]


def test_orbit_path_factor_is_more_cinematic_than_default_circle() -> None:
    assert ORBIT_PATH_FACTOR > 1.0
    assert ORBIT_HEIGHT_SWING_RATIO > 0.0


def test_build_orbit_path_varies_camera_height() -> None:
    scene = {
        "canvas": {"width": 1000, "height": 800},
        "discs": [
            {"x": 500.0, "y": 400.0, "z": 10.0, "radius": 20.0, "thickness": 10.0},
            {"x": 600.0, "y": 420.0, "z": 20.0, "radius": 30.0, "thickness": 8.0},
        ],
    }

    path = build_orbit_path(None, preview_bounds(scene), n_points=24)
    z_values = [float(point[2]) for point in path.points]

    assert max(z_values) > min(z_values)


def test_resolve_material_style_supports_new_translucent_and_glow_styles() -> None:
    translucent = resolve_material_style("translucent_glass")
    glow = resolve_material_style("glow_coral")

    assert translucent.opacity_cap < 0.7
    assert glow.halo_opacity > 0.0


def test_resolve_scene_from_args_supports_word_and_scene(tmp_path: Path) -> None:
    scene_file = tmp_path / "custom_scene.json"
    screenshot_file = tmp_path / "custom_preview.png"
    orbit_file = tmp_path / "custom_orbit.gif"
    args = type("Args", (), {"word": None, "scene": str(scene_file), "screenshot": str(screenshot_file), "orbit_file": str(orbit_file)})()

    paths = resolve_scene_from_args(args)

    assert paths.scene_path == scene_file.resolve()
    assert paths.screenshot_path == screenshot_file.resolve()
    assert paths.orbit_preview_path == scene_file.resolve().with_name("preview_3d_orbit_preview.png")
    assert paths.orbit_path == orbit_file.resolve()


def test_resolve_scene_from_args_uses_default_orbit_path_for_word() -> None:
    args = type("Args", (), {"word": "aaron", "scene": None, "screenshot": None, "orbit_file": None, "material": DEFAULT_MATERIAL})()

    paths = resolve_scene_from_args(args)

    assert paths.scene_path.parent.name == "aaron"
    assert paths.orbit_preview_path.name == "preview_3d_orbit_preview.png"
    assert paths.orbit_path.name == "preview_3d_orbit.gif"


def test_resolve_scene_from_args_uses_material_specific_paths() -> None:
    args = type("Args", (), {"word": "aaron", "scene": None, "screenshot": None, "orbit_file": None, "material": "satin_brass"})()

    paths = resolve_scene_from_args(args)

    assert paths.screenshot_path.name == "preview_3d_satin_brass.png"
    assert paths.orbit_preview_path.name == "preview_3d_orbit_preview_satin_brass.png"
    assert paths.orbit_path.name == "preview_3d_orbit_satin_brass.gif"


def test_resolve_scene_from_args_requires_input() -> None:
    args = type("Args", (), {"word": None, "scene": None, "screenshot": None, "material": DEFAULT_MATERIAL})()

    with pytest.raises(ValueError, match="Provide either --word or --scene"):
        resolve_scene_from_args(args)
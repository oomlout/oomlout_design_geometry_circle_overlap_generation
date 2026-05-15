from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "output"
PREVIEW_DEPTH_SCALE = 6.0
PREVIEW_THICKNESS_SCALE = PREVIEW_DEPTH_SCALE
PREVIEW_CONTACT_OVERLAP = 0.75
PREVIEW_VIEW_ANGLE = 22.0
ORBIT_PREVIEW_VIEW_ANGLE = 24.0
ORBIT_PATH_FACTOR = 1.18
ORBIT_VERTICAL_SHIFT_RATIO = 0.16
ORBIT_HEIGHT_SWING_RATIO = 0.34
ORBIT_RADIUS_PULSE_RATIO = 0.08
DEFAULT_MATERIAL = "topo_clay"
SHOWCASE_MATERIALS = ("topo_clay", "frosted_resin", "satin_brass", "translucent_glass", "glow_coral")


@dataclass(frozen=True)
class ScenePaths:
    scene_path: Path
    screenshot_path: Path
    orbit_preview_path: Path
    orbit_path: Path


@dataclass(frozen=True)
class MaterialStyle:
    key: str
    color_lift: float
    tint: tuple[int, int, int] | None
    tint_strength: float
    opacity_floor: float
    opacity_cap: float
    metallic: float
    roughness: float
    specular: float
    specular_power: float
    ambient: float
    diffuse: float
    halo_tint: tuple[int, int, int] | None = None
    halo_opacity: float = 0.0
    halo_radius_offset: float = 0.0
    halo_height_offset: float = 0.0


MATERIAL_STYLES: dict[str, MaterialStyle] = {
    "topo_clay": MaterialStyle(
        key="topo_clay",
        color_lift=0.08,
        tint=(194, 172, 145),
        tint_strength=0.16,
        opacity_floor=1.0,
        opacity_cap=1.0,
        metallic=0.0,
        roughness=0.82,
        specular=0.18,
        specular_power=10.0,
        ambient=0.2,
        diffuse=0.85,
    ),
    "frosted_resin": MaterialStyle(
        key="frosted_resin",
        color_lift=0.16,
        tint=(230, 238, 244),
        tint_strength=0.1,
        opacity_floor=0.86,
        opacity_cap=0.94,
        metallic=0.02,
        roughness=0.2,
        specular=0.72,
        specular_power=22.0,
        ambient=0.26,
        diffuse=0.76,
    ),
    "satin_brass": MaterialStyle(
        key="satin_brass",
        color_lift=0.1,
        tint=(201, 168, 92),
        tint_strength=0.42,
        opacity_floor=1.0,
        opacity_cap=1.0,
        metallic=0.58,
        roughness=0.32,
        specular=0.78,
        specular_power=24.0,
        ambient=0.24,
        diffuse=0.8,
    ),
    "translucent_glass": MaterialStyle(
        key="translucent_glass",
        color_lift=0.22,
        tint=(194, 234, 245),
        tint_strength=0.28,
        opacity_floor=0.42,
        opacity_cap=0.62,
        metallic=0.0,
        roughness=0.06,
        specular=0.92,
        specular_power=30.0,
        ambient=0.32,
        diffuse=0.62,
    ),
    "glow_coral": MaterialStyle(
        key="glow_coral",
        color_lift=0.3,
        tint=(255, 136, 102),
        tint_strength=0.42,
        opacity_floor=0.82,
        opacity_cap=0.94,
        metallic=0.0,
        roughness=0.18,
        specular=0.25,
        specular_power=12.0,
        ambient=0.7,
        diffuse=0.42,
        halo_tint=(255, 142, 112),
        halo_opacity=0.12,
        halo_radius_offset=6.0,
        halo_height_offset=4.0,
    ),
}


def slugify_word(word: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", word.strip().lower()).strip("_")
    if not slug:
        raise ValueError("A word is required to resolve the 3D scene path.")
    return slug


def scene_paths_for_word(word: str, output_root: Path = OUTPUT_ROOT) -> ScenePaths:
    slug = slugify_word(word)
    folder = output_root / slug
    return ScenePaths(
        scene_path=folder / "scene_3d.json",
        screenshot_path=folder / "preview_3d.png",
        orbit_preview_path=folder / "preview_3d_orbit_preview.png",
        orbit_path=folder / "preview_3d_orbit.gif",
    )


def material_output_name(material: str, base_name: str, suffix: str) -> str:
    if material == DEFAULT_MATERIAL:
        return f"{base_name}.{suffix}"
    return f"{base_name}_{material}.{suffix}"


def resolve_material_style(material: str) -> MaterialStyle:
    try:
        return MATERIAL_STYLES[material]
    except KeyError as exc:
        available = ", ".join(sorted(MATERIAL_STYLES))
        raise ValueError(f"Unknown material '{material}'. Choose from: {available}") from exc


def load_scene(scene_path: Path) -> dict:
    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_path}")
    return json.loads(scene_path.read_text(encoding="utf-8"))


def orbit_preview_output_name(material: str) -> str:
    return material_output_name(material, "preview_3d_orbit_preview", "png")


def scene_bounds(scene: dict) -> dict[str, float]:
    discs = scene.get("discs", [])
    if not discs:
        raise ValueError("The 3D scene contains no discs to preview.")

    min_x = min(disc["x"] - disc["radius"] for disc in discs)
    max_x = max(disc["x"] + disc["radius"] for disc in discs)
    min_y = min(disc["y"] - disc["radius"] for disc in discs)
    max_y = max(disc["y"] + disc["radius"] for disc in discs)
    min_z = min(disc["z"] - (disc["thickness"] / 2) for disc in discs)
    max_z = max(disc["z"] + (disc["thickness"] / 2) for disc in discs)
    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "min_z": min_z,
        "max_z": max_z,
    }


def plot_coordinates(disc: dict, canvas: dict) -> tuple[float, float, float]:
    x = disc["x"] - (canvas["width"] / 2)
    y = (canvas["height"] / 2) - disc["y"]
    z = disc["z"] * PREVIEW_DEPTH_SCALE
    return (x, y, z)


def preview_thickness(disc: dict) -> float:
    return (disc["thickness"] * PREVIEW_THICKNESS_SCALE) + PREVIEW_CONTACT_OVERLAP


def preview_bounds(scene: dict) -> dict[str, float]:
    canvas = scene["canvas"]
    discs = scene["discs"]
    if not discs:
        raise ValueError("The 3D scene contains no discs to preview.")

    centers = [plot_coordinates(disc, canvas) for disc in discs]
    min_x = min(center_x - disc["radius"] for (center_x, _, _), disc in zip(centers, discs))
    max_x = max(center_x + disc["radius"] for (center_x, _, _), disc in zip(centers, discs))
    min_y = min(center_y - disc["radius"] for (_, center_y, _), disc in zip(centers, discs))
    max_y = max(center_y + disc["radius"] for (_, center_y, _), disc in zip(centers, discs))
    min_z = min(center_z - (preview_thickness(disc) / 2) for (_, _, center_z), disc in zip(centers, discs))
    max_z = max(center_z + (preview_thickness(disc) / 2) for (_, _, center_z), disc in zip(centers, discs))
    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "min_z": min_z,
        "max_z": max_z,
    }


def scene_center(bounds: dict[str, float]) -> tuple[float, float, float]:
    return (
        (bounds["min_x"] + bounds["max_x"]) / 2,
        (bounds["min_y"] + bounds["max_y"]) / 2,
        (bounds["min_z"] + bounds["max_z"]) / 2,
    )


def cinematic_target(bounds: dict[str, float]) -> tuple[float, float, float]:
    center_x, center_y, center_z = scene_center(bounds)
    span_x = bounds["max_x"] - bounds["min_x"]
    span_y = bounds["max_y"] - bounds["min_y"]
    span_z = bounds["max_z"] - bounds["min_z"]
    horizontal_span = max(span_x, span_y)
    return (
        center_x - horizontal_span * 0.06,
        center_y + horizontal_span * 0.04,
        center_z + span_z * 0.22,
    )


def default_camera(bounds: dict[str, float]) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    center_x, center_y, center_z = scene_center(bounds)
    span_x = bounds["max_x"] - bounds["min_x"]
    span_y = bounds["max_y"] - bounds["min_y"]
    span_z = bounds["max_z"] - bounds["min_z"]
    horizontal_span = max(span_x, span_y)
    distance = horizontal_span * 1.12 + span_z * 2.4 + 220.0
    target = cinematic_target(bounds)

    return (
        (center_x + distance * 0.84, center_y - distance * 0.94, center_z + distance * 0.24),
        target,
        (0.0, 0.0, 1.0),
    )


def build_orbit_path(plotter, bounds: dict[str, float], n_points: int):
    pv = _require_pyvista()
    center_x, center_y, center_z = scene_center(bounds)
    span_x = bounds["max_x"] - bounds["min_x"]
    span_y = bounds["max_y"] - bounds["min_y"]
    span_z = bounds["max_z"] - bounds["min_z"]
    base_radius = max(span_x, span_y) * ORBIT_PATH_FACTOR * 0.5
    vertical_base = center_z + (span_z * ORBIT_VERTICAL_SHIFT_RATIO)
    vertical_swing = max(span_z * ORBIT_HEIGHT_SWING_RATIO, 36.0)

    points: list[tuple[float, float, float]] = []
    for index in range(max(n_points, 12)):
        angle = (index / max(n_points, 12)) * math.tau
        radius_scale = 1.0 + (math.sin(angle * 2.0 - 0.35) * ORBIT_RADIUS_PULSE_RATIO)
        radius_x = base_radius * radius_scale * 1.06
        radius_y = base_radius * radius_scale * 0.78
        x = center_x + math.cos(angle) * radius_x
        y = center_y + math.sin(angle) * radius_y - (base_radius * 0.22)
        z = vertical_base + math.sin(angle - 0.6) * vertical_swing + math.cos(angle * 2.0 + 0.3) * (vertical_swing * 0.18)
        points.append((x, y, z))

    points.append(points[0])
    return pv.Spline(points, n_points=len(points) * 12)


def orbit_preview_camera(path, bounds: dict[str, float]) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    first_point = tuple(float(value) for value in path.points[0])
    return (
        first_point,
        cinematic_target(bounds),
        (0.0, 0.0, 1.0),
    )


def _normalize_color(color: list[int]) -> tuple[float, float, float]:
    return tuple(component / 255 for component in color)


def _lift_color(color: list[int], amount: float = 0.18) -> tuple[float, float, float]:
    base = _normalize_color(color)
    return tuple(min(1.0, component * (1.0 - amount) + amount) for component in base)


def _blend_color(
    base: tuple[float, float, float],
    tint: tuple[int, int, int] | None,
    strength: float,
) -> tuple[float, float, float]:
    if tint is None or strength <= 0:
        return base
    tint_color = _normalize_color(list(tint))
    return tuple((component * (1.0 - strength)) + (tint_component * strength) for component, tint_component in zip(base, tint_color))


def material_color(color: list[int], material: MaterialStyle) -> tuple[float, float, float]:
    lifted = _lift_color(color, amount=material.color_lift)
    return _blend_color(lifted, material.tint, material.tint_strength)


def material_opacity(disc: dict, material: MaterialStyle) -> float:
    return min(max(disc["opacity"], material.opacity_floor), material.opacity_cap)


def material_halo_color(material: MaterialStyle) -> tuple[float, float, float] | None:
    if material.halo_tint is None:
        return None
    return _normalize_color(list(material.halo_tint))


def _require_pyvista():
    try:
        import pyvista as pv
    except ImportError as exc:
        raise RuntimeError(
            "PyVista is required for 3D previewing. Install dependencies with setup.bat/setup.sh or pip install -r requirements.txt."
        ) from exc
    return pv


def _build_plotter(scene: dict, off_screen: bool, material_name: str = DEFAULT_MATERIAL):
    pv = _require_pyvista()
    bounds = preview_bounds(scene)
    canvas = scene["canvas"]
    discs = scene["discs"]
    material = resolve_material_style(material_name)

    plotter = pv.Plotter(window_size=(1600, 1000), off_screen=off_screen)
    plotter.set_background("#e7dfd2", top="#1b2230")
    plotter.enable_anti_aliasing("ssaa")

    for disc in discs:
        if material.halo_opacity > 0 and material.halo_tint is not None:
            halo = pv.Cylinder(
                center=plot_coordinates(disc, canvas),
                direction=(0.0, 0.0, 1.0),
                radius=disc["radius"] + material.halo_radius_offset,
                height=preview_thickness(disc) + material.halo_height_offset,
                resolution=96,
                capping=True,
            )
            plotter.add_mesh(
                halo,
                color=material_halo_color(material),
                opacity=material.halo_opacity,
                smooth_shading=True,
                lighting=False,
            )
        cylinder = pv.Cylinder(
            center=plot_coordinates(disc, canvas),
            direction=(0.0, 0.0, 1.0),
            radius=disc["radius"],
            height=preview_thickness(disc),
            resolution=96,
            capping=True,
        )
        plotter.add_mesh(
            cylinder,
            color=material_color(disc["color"], material),
            opacity=material_opacity(disc, material),
            smooth_shading=True,
            pbr=True,
            metallic=material.metallic,
            roughness=material.roughness,
            ambient=material.ambient,
            diffuse=material.diffuse,
            specular=material.specular,
            specular_power=material.specular_power,
        )

    key_light = pv.Light(position=(420, -760, 720), focal_point=(0, 0, 80), color="#fff0d6", intensity=1.35)
    rim_light = pv.Light(position=(-860, 520, 880), focal_point=(0, 0, 40), color="#afc8ff", intensity=0.85)
    fill_light = pv.Light(position=(120, 220, 980), focal_point=(0, 0, 0), color="#f7fbff", intensity=0.4)
    bounce_light = pv.Light(position=(0, 980, 240), focal_point=(0, 0, 30), color="#f6d9be", intensity=0.22)
    plotter.add_light(key_light)
    plotter.add_light(rim_light)
    plotter.add_light(fill_light)
    plotter.add_light(bounce_light)
    plotter.camera_position = default_camera(bounds)
    plotter.camera.SetViewAngle(PREVIEW_VIEW_ANGLE)

    return plotter, bounds


def render_scene(
    scene_path: Path,
    screenshot_path: Path | None = None,
    show: bool = True,
    material_name: str = DEFAULT_MATERIAL,
) -> Path | None:
    scene = load_scene(scene_path)

    if screenshot_path is not None:
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Rendering still preview: {screenshot_path}")

    plotter, _bounds = _build_plotter(scene, off_screen=not show, material_name=material_name)

    if show:
        plotter.show(auto_close=False)
        if screenshot_path is not None:
            plotter.screenshot(str(screenshot_path))
        plotter.close()
    elif screenshot_path is not None:
        plotter.screenshot(str(screenshot_path))
        plotter.close()

    return screenshot_path


def render_orbit_preview(
    scene_path: Path,
    orbit_preview_path: Path,
    n_points: int = 48,
    material_name: str = DEFAULT_MATERIAL,
) -> Path:
    scene = load_scene(scene_path)
    orbit_preview_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Rendering orbit preview: {orbit_preview_path}")
    plotter, bounds = _build_plotter(scene, off_screen=True, material_name=material_name)
    path = build_orbit_path(plotter, bounds, n_points=n_points)
    plotter.camera_position = orbit_preview_camera(path, bounds)
    plotter.camera.SetViewAngle(ORBIT_PREVIEW_VIEW_ANGLE)
    plotter.screenshot(str(orbit_preview_path))
    plotter.close()
    return orbit_preview_path


def render_orbit_animation(
    scene_path: Path,
    orbit_path: Path,
    n_points: int = 48,
    fps: int = 18,
    material_name: str = DEFAULT_MATERIAL,
) -> Path:
    scene = load_scene(scene_path)
    orbit_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Rendering orbit animation: {orbit_path}")
    plotter, bounds = _build_plotter(scene, off_screen=True, material_name=material_name)
    plotter.open_gif(str(orbit_path), fps=fps)
    path = build_orbit_path(plotter, bounds, n_points=n_points)
    plotter.camera_position = orbit_preview_camera(path, bounds)
    plotter.camera.SetViewAngle(ORBIT_PREVIEW_VIEW_ANGLE)
    plotter.orbit_on_path(
        path=path,
        write_frames=True,
        viewup=(0.0, 0.0, 1.0),
        threaded=False,
        progress_bar=False,
    )
    plotter.close()
    return orbit_path


def render_showcase_set(
    scene_path: Path,
    materials: tuple[str, ...] = SHOWCASE_MATERIALS,
    orbit: bool = True,
    n_points: int = 48,
    fps: int = 18,
) -> list[Path]:
    outputs: list[Path] = []
    for material_name in materials:
        print(f"Preparing 3D showcase material: {material_name}")
        paths = ScenePaths(
            scene_path=scene_path,
            screenshot_path=scene_path.with_name(material_output_name(material_name, "preview_3d", "png")),
            orbit_preview_path=scene_path.with_name(orbit_preview_output_name(material_name)),
            orbit_path=scene_path.with_name(material_output_name(material_name, "preview_3d_orbit", "gif")),
        )
        screenshot = render_scene(
            paths.scene_path,
            screenshot_path=paths.screenshot_path,
            show=False,
            material_name=material_name,
        )
        if screenshot is not None:
            outputs.append(screenshot)
        outputs.append(
            render_orbit_preview(
                paths.scene_path,
                paths.orbit_preview_path,
                n_points=n_points,
                material_name=material_name,
            )
        )
        if orbit:
            outputs.append(
                render_orbit_animation(
                    paths.scene_path,
                    paths.orbit_path,
                    n_points=n_points,
                    fps=fps,
                    material_name=material_name,
                )
            )
    return outputs


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a generated 3D disc scene using PyVista.")
    parser.add_argument("--word", help="Word/output folder to preview, such as joy or aaron.")
    parser.add_argument("--scene", help="Direct path to a scene_3d.json file.")
    parser.add_argument("--screenshot", help="Optional path for a saved preview image.")
    parser.add_argument("--material", default=DEFAULT_MATERIAL, choices=sorted(MATERIAL_STYLES), help="Material preset to use for the render.")
    parser.add_argument("--all-materials", action="store_true", help="Render screenshots, and optionally orbit GIFs, for all showcase materials.")
    parser.add_argument("--orbit-preview", action="store_true", help="Write a still image from the orbit camera framing.")
    parser.add_argument("--orbit", action="store_true", help="Write an orbit GIF animation.")
    parser.add_argument("--orbit-file", help="Optional path for the orbit GIF output.")
    parser.add_argument("--orbit-frames", type=int, default=48, help="Number of frames in the orbit animation.")
    parser.add_argument("--orbit-fps", type=int, default=18, help="Frames per second for the orbit GIF.")
    parser.add_argument("--no-show", action="store_true", help="Render only a screenshot without opening the interactive viewer.")
    return parser


def resolve_scene_from_args(args: argparse.Namespace) -> ScenePaths:
    material_name = getattr(args, "material", DEFAULT_MATERIAL)
    screenshot_name = material_output_name(material_name, "preview_3d", "png")
    orbit_preview_name = orbit_preview_output_name(material_name)
    orbit_name = material_output_name(material_name, "preview_3d_orbit", "gif")
    if args.scene:
        scene_path = Path(args.scene).resolve()
        screenshot_path = Path(args.screenshot).resolve() if args.screenshot else scene_path.with_name(screenshot_name)
        orbit_preview_path = scene_path.with_name(orbit_preview_name)
        orbit_path = Path(args.orbit_file).resolve() if getattr(args, "orbit_file", None) else scene_path.with_name(orbit_name)
        return ScenePaths(scene_path=scene_path, screenshot_path=screenshot_path, orbit_preview_path=orbit_preview_path, orbit_path=orbit_path)
    if args.word:
        paths = scene_paths_for_word(args.word)
        if args.screenshot:
            screenshot_path = Path(args.screenshot).resolve()
        else:
            screenshot_path = paths.screenshot_path.with_name(screenshot_name)
        orbit_preview_path = paths.orbit_preview_path.with_name(orbit_preview_name)
        if getattr(args, "orbit_file", None):
            orbit_path = Path(args.orbit_file).resolve()
        else:
            orbit_path = paths.orbit_path.with_name(orbit_name)
        return ScenePaths(scene_path=paths.scene_path, screenshot_path=screenshot_path, orbit_preview_path=orbit_preview_path, orbit_path=orbit_path)
    raise ValueError("Provide either --word or --scene.")


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    paths = resolve_scene_from_args(args)
    if args.all_materials:
        outputs = render_showcase_set(
            paths.scene_path,
            orbit=True,
            n_points=args.orbit_frames,
            fps=args.orbit_fps,
        )
        for output in outputs:
            print(output)
        return
    screenshot = render_scene(
        paths.scene_path,
        screenshot_path=paths.screenshot_path,
        show=not args.no_show,
        material_name=args.material,
    )
    if screenshot is not None:
        print(screenshot)
    if args.orbit_preview or args.orbit:
        orbit_preview_path = render_orbit_preview(
            paths.scene_path,
            paths.orbit_preview_path,
            n_points=args.orbit_frames,
            material_name=args.material,
        )
        print(orbit_preview_path)
    if args.orbit:
        orbit_path = render_orbit_animation(
            paths.scene_path,
            paths.orbit_path,
            n_points=args.orbit_frames,
            fps=args.orbit_fps,
            material_name=args.material,
        )
        print(orbit_path)


if __name__ == "__main__":
    main()
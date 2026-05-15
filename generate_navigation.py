from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "output"


@dataclass(frozen=True)
class GalleryItem:
    name: str
    slug: str
    folder: Path
    final_image: Path | None
    animation: Path | None
    metadata: Path | None
    circles: Path | None
    level_dir: Path | None
    frame_count: int
    level_count: int
    input_text: str | None


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "gallery-item"


def read_effective_config(metadata_path: Path | None) -> dict:
    if metadata_path is None or not metadata_path.exists():
        return {}
    with metadata_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    return data if isinstance(data, dict) else {}


def collect_gallery_items(output_root: Path) -> list[GalleryItem]:
    if not output_root.exists():
        return []

    items: list[GalleryItem] = []
    for folder in sorted(path for path in output_root.iterdir() if path.is_dir()):
        metadata = folder / "effective_config.yaml"
        circles = folder / "circles.yaml"
        config_data = read_effective_config(metadata)
        final_name = config_data.get("outputs", {}).get("final_filename", "working.png")
        animation_name = config_data.get("outputs", {}).get("animation_filename", "working.gif")
        final_image = folder / str(final_name)
        animation = folder / str(animation_name)
        final_image = final_image if final_image.exists() else None
        animation = animation if animation.exists() else None

        frame_prefix = config_data.get("outputs", {}).get("sequence_prefix", "working_")
        frames = sorted(folder.glob(f"{frame_prefix}*.png"))

        final_stem = final_image.stem if final_image is not None else "working"
        level_dir = folder / final_stem
        level_dir = level_dir if level_dir.exists() else None
        level_count = len(list(level_dir.glob("level_*.png"))) if level_dir is not None else 0

        items.append(
            GalleryItem(
                name=folder.name,
                slug=slugify(folder.name),
                folder=folder,
                final_image=final_image,
                animation=animation,
                metadata=metadata if metadata.exists() else None,
                circles=circles if circles.exists() else None,
                level_dir=level_dir,
                frame_count=len(frames),
                level_count=level_count,
                input_text=config_data.get("input_text"),
            )
        )

    return items


def render_index(items: list[GalleryItem]) -> str:
    cards: list[str] = []
    for item in items:
        preview = item.animation or item.final_image
        preview_markup = ""
        if preview is not None:
            preview_markup = f'<img src="./{item.name}/{preview.name}" alt="{item.name} preview" width="100%">'
        subtitle = item.input_text or item.name
        cards.append(
            "\n".join(
                [
                    '<table width="100%">',
                    "<tr>",
                    f'<td width="48%" valign="top">{preview_markup}<br><br><strong><a href="./{item.name}/README.md">{item.name}</a></strong><br>{subtitle}<br>Frames: {item.frame_count} | Levels: {item.level_count}</td>',
                    "</tr>",
                    "</table>",
                ]
            )
        )

    cards_markup = "\n\n".join(cards) if cards else "No generated output folders were found under `output/`."

    return f"""# Generated Gallery

Browse the generated circle-overlap runs from this markdown gallery.

This navigation is generated automatically from the folders inside `output/`.

## Runs

{cards_markup}
"""


def render_item_page(item: GalleryItem) -> str:
    preview_sections: list[str] = []
    if item.animation is not None:
        preview_sections.append(f"![{item.name} animation](./{item.animation.name})")
    if item.final_image is not None:
        preview_sections.append(f"![{item.name} final](./{item.final_image.name})")

    levels_markup = ""
    if item.level_dir is not None:
        level_paths = sorted(item.level_dir.glob("level_*.png"))[:6]
        if level_paths:
            level_images = "\n".join(
                f'![{level_path.stem}](./{item.level_dir.name}/{level_path.name})'
                for level_path in level_paths
            )
            levels_markup = f"""
## Level Previews

{level_images}
"""

    file_links: list[str] = []
    if item.metadata is not None:
        file_links.append(f"- [effective_config.yaml](./{item.metadata.name})")
    if item.circles is not None:
        file_links.append(f"- [circles.yaml](./{item.circles.name})")
    if item.final_image is not None:
        file_links.append(f"- [final image](./{item.final_image.name})")
    if item.animation is not None:
        file_links.append(f"- [animation](./{item.animation.name})")

    files_markup = "\n".join(file_links) if file_links else "- No files detected"

    return f"""# {item.name}

[Back to output gallery](../README.md)

## Summary

- Input text: `{item.input_text or item.name}`
- Frame count: `{item.frame_count}`
- Level count: `{item.level_count}`

## Preview

{chr(10).join(preview_sections) if preview_sections else 'No preview assets were found.'}

## Files

{files_markup}
{levels_markup}
"""


def write_navigation(output_root: Path = OUTPUT_ROOT) -> list[Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    items = collect_gallery_items(output_root)

    written_files: list[Path] = []
    index_path = output_root / "README.md"
    index_path.write_text(render_index(items), encoding="utf-8")
    written_files.append(index_path)

    for item in items:
        page_path = item.folder / "README.md"
        page_path.write_text(render_item_page(item), encoding="utf-8")
        written_files.append(page_path)

    return written_files


if __name__ == "__main__":
    for file_path in write_navigation():
        print(file_path)
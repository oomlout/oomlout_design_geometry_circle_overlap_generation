from pathlib import Path

import yaml

from generate_navigation import write_navigation


def test_write_navigation_creates_index_and_detail_pages(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo_run"
    run_dir.mkdir(parents=True)

    (run_dir / "working.png").write_bytes(b"png")
    (run_dir / "working.gif").write_bytes(b"gif")
    (run_dir / "working_0.png").write_bytes(b"frame")
    levels_dir = run_dir / "working"
    levels_dir.mkdir()
    (levels_dir / "level_1.png").write_bytes(b"level")

    effective_config = {
        "input_text": "demo",
        "outputs": {
            "final_filename": "working.png",
            "animation_filename": "working.gif",
            "sequence_prefix": "working_",
        },
    }
    with (run_dir / "effective_config.yaml").open("w", encoding="utf-8") as file:
        yaml.safe_dump(effective_config, file, sort_keys=False)
    with (run_dir / "circles.yaml").open("w", encoding="utf-8") as file:
        yaml.safe_dump([{"x": 1, "y": 1, "radius": 2}], file, sort_keys=False)

    navigation_root = tmp_path / "navigation"
    written_files = write_navigation(output_root=output_root, navigation_root=navigation_root)

    index_path = navigation_root / "index.md"
    detail_path = navigation_root / "demo-run.md"

    assert index_path in written_files
    assert detail_path in written_files
    assert "demo_run" in index_path.read_text(encoding="utf-8")
    assert "working.gif" in detail_path.read_text(encoding="utf-8")
    assert "level_1.png" in detail_path.read_text(encoding="utf-8")
from __future__ import annotations

from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = SCRIPT_DIR.parent
AUDIO_DIR = ROOT_DIR / "assets" / "audio"


def resolve_input_path(input_path: Path) -> Path:
    if input_path.is_absolute():
        return input_path

    repo_relative = ROOT_DIR / input_path
    if repo_relative.exists():
        return repo_relative.resolve()
    return input_path.resolve()


def default_output_path(input_path: Path) -> Path:
    return (AUDIO_DIR / f"{input_path.stem}.mp3").resolve()


def resolve_output_path(input_path: Path, output_path: Path | None) -> Path:
    if output_path is None:
        return default_output_path(input_path)
    if output_path.is_absolute():
        return output_path
    return (ROOT_DIR / output_path).resolve()


def path_to_site_url(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(ROOT_DIR)
    except ValueError as exc:
        raise ValueError(
            f"Audio path must be inside the repository to insert a site URL: {path}"
        ) from exc
    return "/" + relative.as_posix()

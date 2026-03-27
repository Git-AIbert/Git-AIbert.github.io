from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .paths import ROOT_DIR, resolve_input_path
from .workflow import generate_audio, generate_audio_and_update_post


def resolve_optional_dir(path: Path | None) -> Path | None:
    if path is None:
        return None
    if path.is_absolute():
        return path.resolve()
    return (ROOT_DIR / path).resolve()


def output_path_for(
    input_path: Path, output_path: Path | None, output_dir: Path | None
) -> Path | None:
    if output_path is not None:
        if output_path.is_absolute():
            return output_path.resolve()
        return (ROOT_DIR / output_path).resolve()
    if output_dir is None:
        return None
    return (output_dir / f"{input_path.stem}.mp3").resolve()


def cleaned_text_path_for(
    input_path: Path, cleaned_text_out: Path | None, cleaned_text_dir: Path | None
) -> Path | None:
    if cleaned_text_out is not None:
        if cleaned_text_out.is_absolute():
            return cleaned_text_out.resolve()
        return (ROOT_DIR / cleaned_text_out).resolve()
    if cleaned_text_dir is None:
        return None
    return (cleaned_text_dir / f"{input_path.stem}.txt").resolve()


def process_posts(
    input_paths: Sequence[Path],
    output_path: Path | None,
    output_dir: Path | None,
    update_post: bool,
    language: str,
    device: str,
    speed: float,
    speaker: str | None,
    replacement_file: Path | None,
    keep_ascii: bool,
    cleaned_text_out: Path | None,
    cleaned_text_dir: Path | None,
) -> list[Path]:
    resolved_output_dir = resolve_optional_dir(output_dir)
    resolved_cleaned_text_dir = resolve_optional_dir(cleaned_text_dir)
    outputs: list[Path] = []

    for raw_input in input_paths:
        resolved_input = resolve_input_path(raw_input)
        resolved_output = output_path_for(resolved_input, output_path, resolved_output_dir)
        resolved_cleaned_text = cleaned_text_path_for(
            resolved_input, cleaned_text_out, resolved_cleaned_text_dir
        )
        runner = generate_audio_and_update_post if update_post else generate_audio
        outputs.append(
            runner(
                input_path=resolved_input,
                output_path=resolved_output,
                language=language,
                device=device,
                speed=speed,
                speaker=speaker,
                replacement_file=replacement_file,
                keep_ascii=keep_ascii,
                cleaned_text_out=resolved_cleaned_text,
            )
        )

    return outputs

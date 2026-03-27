from __future__ import annotations

from pathlib import Path

from .paths import path_to_site_url, resolve_input_path, resolve_output_path
from .post_update import update_post_audio_player
from .synthesis import resolve_device, synthesize_audio
from .text_cleaning import prepare_text


def write_cleaned_text(path: Path | None, text: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def generate_audio(
    input_path: Path,
    output_path: Path | None,
    language: str,
    device: str,
    speed: float,
    speaker: str | None,
    replacement_file: Path | None,
    keep_ascii: bool,
    cleaned_text_out: Path | None,
) -> Path:
    resolved_input = resolve_input_path(input_path)
    resolved_output = resolve_output_path(resolved_input, output_path)
    text = prepare_text(
        input_path=resolved_input,
        language=language,
        replacement_file=replacement_file,
        keep_ascii=keep_ascii,
    )
    write_cleaned_text(cleaned_text_out, text)
    resolved_device = resolve_device(device)
    print(f"Using device: {resolved_device}")
    print(f"Generating audio: {resolved_input} -> {resolved_output}")
    synthesize_audio(
        text=text,
        output_path=resolved_output,
        language=language,
        device=resolved_device,
        speed=speed,
        speaker=speaker,
    )
    print(f"Done: {resolved_output}")
    return resolved_output


def generate_audio_and_update_post(
    input_path: Path,
    output_path: Path | None,
    language: str,
    device: str,
    speed: float,
    speaker: str | None,
    replacement_file: Path | None,
    keep_ascii: bool,
    cleaned_text_out: Path | None,
) -> Path:
    resolved_input = resolve_input_path(input_path)
    resolved_output = generate_audio(
        input_path=resolved_input,
        output_path=output_path,
        language=language,
        device=device,
        speed=speed,
        speaker=speaker,
        replacement_file=replacement_file,
        keep_ascii=keep_ascii,
        cleaned_text_out=cleaned_text_out,
    )
    update_post_audio_player(resolved_input, path_to_site_url(resolved_output))
    print(f"Updated post audio player: {resolved_input}")
    return resolved_output


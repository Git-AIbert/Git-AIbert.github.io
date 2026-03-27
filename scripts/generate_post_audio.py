#!/usr/bin/env python3

from __future__ import annotations

from tts_tool.batch import process_posts
from tts_tool.cli import parse_post_audio_args
from tts_tool.runtime import ensure_runtime_python


def main() -> None:
    ensure_runtime_python()
    args = parse_post_audio_args()
    process_posts(
        input_paths=args.inputs,
        output_path=args.output,
        output_dir=args.output_dir,
        update_post=not args.audio_only,
        language=args.language,
        device=args.device,
        speed=args.speed,
        speaker=args.speaker,
        replacement_file=args.replacement_file,
        keep_ascii=args.keep_ascii,
        cleaned_text_out=args.cleaned_text_out,
        cleaned_text_dir=args.cleaned_text_dir,
    )


if __name__ == "__main__":
    main()

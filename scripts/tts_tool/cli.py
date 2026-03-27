from __future__ import annotations

import argparse
from pathlib import Path


def add_common_options(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--language",
        "-l",
        default="ZH",
        choices=["ZH", "EN", "ES", "FR", "JP", "KR"],
        help="MeloTTS language code",
    )
    parser.add_argument(
        "--device",
        "-d",
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Inference device",
    )
    parser.add_argument(
        "--speed",
        "-s",
        type=float,
        default=1.0,
        help="Speech speed",
    )
    parser.add_argument(
        "--speaker",
        help="Optional speaker id. Defaults to the first speaker for the selected language.",
    )
    parser.add_argument(
        "--replacement-file",
        type=Path,
        help="Optional JSON file with additional text replacements",
    )
    parser.add_argument(
        "--keep-ascii",
        action="store_true",
        help="Keep remaining ASCII words instead of stripping them in Chinese mode",
    )
    parser.add_argument(
        "--cleaned-text-out",
        type=Path,
        help="Optional path to write the cleaned text used for synthesis",
    )
    return parser


def parse_post_audio_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate article audio for one or more posts, and optionally insert or update their audio players."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="One or more input markdown or text files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output audio file for a single input",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional output directory for generated audio files. Defaults to assets/audio/<input filename>.mp3",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Generate audio without inserting or updating the player in the post",
    )
    parser.add_argument(
        "--cleaned-text-dir",
        type=Path,
        help="Optional directory to write cleaned text files for each input",
    )
    add_common_options(parser)
    args = parser.parse_args()
    if len(args.inputs) > 1 and args.output is not None:
        parser.error("--output can only be used when exactly one input is provided")
    if len(args.inputs) > 1 and args.cleaned_text_out is not None:
        parser.error(
            "--cleaned-text-out can only be used when exactly one input is provided"
        )
    return args

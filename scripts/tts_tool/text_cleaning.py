from __future__ import annotations

import json
import re
from pathlib import Path


DEFAULT_REPLACEMENTS = {
    "Shelly Kagan": "谢利·卡根",
    "Professor Kagan": "卡根教授",
    "Shelly": "谢利",
    "Elisabeth Kübler-Ross": "伊丽莎白·库伯勒-罗斯",
    "Karen": "凯伦",
    "office hour": "答疑时间",
    "credit/D/fail": "记为通过或不通过",
}

GRADE_REPLACEMENTS = {
    "A": "优",
    "B": "良",
    "C": "中",
    "D": "及格",
    "F": "不及格",
}

ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.\-/]*")
FRONT_MATTER_RE = re.compile(r"^---\n.*?\n---\n+", re.S)
FENCED_CODE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
HTML_RE = re.compile(r"<[^>]+>")


def load_replacements(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Replacement file must contain a JSON object.")
    return {str(k): str(v) for k, v in data.items()}


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER_RE.sub("", text, count=1)


def clean_markdown(text: str) -> str:
    text = strip_front_matter(text)
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub(r"\1", text)
    text = LINK_RE.sub(r"\1", text)
    text = HTML_RE.sub("", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_text(input_path: Path) -> str:
    text = input_path.read_text(encoding="utf-8")
    if input_path.suffix.lower() in {".md", ".qmd"}:
        text = clean_markdown(text)
    return text


def apply_replacements(text: str, replacements: dict[str, str]) -> str:
    for source, target in replacements.items():
        text = text.replace(source, target)
    for source, target in GRADE_REPLACEMENTS.items():
        text = re.sub(rf"\b{re.escape(source)}\b", target, text)
    return text


def normalize_for_chinese(text: str, keep_ascii: bool) -> str:
    if not keep_ascii:
        text = ASCII_TOKEN_RE.sub(" ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def prepare_text(
    input_path: Path,
    language: str,
    replacement_file: Path | None = None,
    keep_ascii: bool = False,
) -> str:
    text = load_text(input_path)
    replacements = DEFAULT_REPLACEMENTS | load_replacements(replacement_file)
    text = apply_replacements(text, replacements)

    if language == "ZH":
        text = normalize_for_chinese(text, keep_ascii=keep_ascii)

    return text


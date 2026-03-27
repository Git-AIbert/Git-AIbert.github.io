from __future__ import annotations

import re
from pathlib import Path


FRONT_MATTER_RE = re.compile(r"^---\n.*?\n---\n*", re.S)
AUDIO_BLOCK_RE = re.compile(
    r'(?ms)^<audio controls preload="none" style="width: 100%;">\n'
    r'  <source src="[^"]+" type="audio/mpeg">\n'
    r"</audio>\n*"
)


def render_audio_block(audio_url: str) -> str:
    return (
        '<audio controls preload="none" style="width: 100%;">\n'
        f'  <source src="{audio_url}" type="audio/mpeg">\n'
        "</audio>\n"
    )


def upsert_audio_player(content: str, audio_url: str) -> str:
    audio_block = render_audio_block(audio_url)
    if AUDIO_BLOCK_RE.search(content):
        return AUDIO_BLOCK_RE.sub(audio_block + "\n", content, count=1)

    match = FRONT_MATTER_RE.match(content)
    if match:
        return content[: match.end()] + "\n" + audio_block + "\n" + content[match.end() :]
    return audio_block + "\n" + content


def update_post_audio_player(post_path: Path, audio_url: str) -> None:
    content = post_path.read_text(encoding="utf-8")
    updated = upsert_audio_player(content, audio_url)
    post_path.write_text(updated, encoding="utf-8")


from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


def resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested

    import torch

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def resolve_cached_model_files(language: str) -> tuple[Path | None, Path | None]:
    repo_id = {
        "ZH": "myshell-ai/MeloTTS-Chinese",
        "EN": "myshell-ai/MeloTTS-English",
        "ES": "myshell-ai/MeloTTS-Spanish",
        "FR": "myshell-ai/MeloTTS-French",
        "JP": "myshell-ai/MeloTTS-Japanese",
        "KR": "myshell-ai/MeloTTS-Korean",
    }[language]
    repo_dir = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{repo_id.replace('/', '--')}"
    snapshots_dir = repo_dir / "snapshots"
    if not snapshots_dir.exists():
        return None, None

    snapshots = sorted(
        (path for path in snapshots_dir.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for snapshot in snapshots:
        config_path = snapshot / "config.json"
        ckpt_path = snapshot / "checkpoint.pth"
        if config_path.exists() and ckpt_path.exists():
            return config_path, ckpt_path
    return None, None


def choose_speaker(speaker_ids: dict[str, int], speaker: str | None) -> int:
    if speaker:
        if speaker not in speaker_ids:
            available = ", ".join(sorted(speaker_ids))
            raise ValueError(f"Unknown speaker '{speaker}'. Available speakers: {available}")
        return speaker_ids[speaker]

    preferred = ("ZH", "EN-Default", "ES", "FR", "JP", "KR")
    for name in preferred:
        if name in speaker_ids:
            return speaker_ids[name]
    return speaker_ids[next(iter(speaker_ids))]


def ensure_ffmpeg() -> None:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("ffmpeg is required to generate mp3 output.") from exc


def build_model(language: str, device: str):
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

    config_path, ckpt_path = resolve_cached_model_files(language)
    if config_path and ckpt_path:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    from melo.api import TTS

    if config_path and ckpt_path:
        return TTS(
            language=language,
            device=device,
            config_path=str(config_path),
            ckpt_path=str(ckpt_path),
        )
    return TTS(language=language, device=device)


def synthesize_audio(
    text: str,
    output_path: Path,
    language: str,
    device: str,
    speed: float,
    speaker: str | None,
) -> None:
    model = build_model(language=language, device=device)
    speaker_id = choose_speaker(model.hps.data.spk2id, speaker)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".wav":
        model.tts_to_file(text, speaker_id, str(output_path), speed=speed)
        return
    if output_path.suffix.lower() != ".mp3":
        raise ValueError("Output file must end with .mp3 or .wav")

    ensure_ffmpeg()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = Path(tmp.name)
    try:
        model.tts_to_file(text, speaker_id, str(wav_path), speed=speed)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(wav_path),
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "4",
                str(output_path),
            ],
            check=True,
        )
    finally:
        wav_path.unlink(missing_ok=True)


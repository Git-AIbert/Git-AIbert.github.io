from __future__ import annotations

import os
import sys
from pathlib import Path


DEFAULT_VENV_PYTHON = Path.home() / "venvs" / "melotts" / "bin" / "python"


def import_available(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def ensure_runtime_python() -> None:
    if os.environ.get("GENERATE_TTS_ACTIVE_PYTHON") == "1":
        return
    if import_available("melo.api"):
        return
    if not DEFAULT_VENV_PYTHON.exists():
        return

    env = os.environ.copy()
    env["GENERATE_TTS_ACTIVE_PYTHON"] = "1"
    os.execvpe(str(DEFAULT_VENV_PYTHON), [str(DEFAULT_VENV_PYTHON), *sys.argv], env)


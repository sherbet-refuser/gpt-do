from pathlib import Path

MODEL = "gpt-4o"

TMP_DIR = Path.cwd() / "tmp"
LOG_DIR = TMP_DIR / "logs"


class GptDont(Exception):
    """Base exception for gpt_do package."""

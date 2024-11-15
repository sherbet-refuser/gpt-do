from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from .action import Action

logger = logging.getLogger(__name__)


class ReadFile(Action["ReadFile.Args", "ReadFile.Output"]):
    """Read a text file into a string given a path.

    Args:
        path: The path to the file.

    Output:
        contents: The contents of the file.
        error: An error message if the file could not be read.
    """

    confirm = False

    class Args(BaseModel):
        path: str

    class Output(BaseModel):
        contents: Optional[str]
        error: Optional[str]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""

        path = Path(args.path)
        if not path.exists():
            logger.error(f"Path doesn't exist: {path!r}")
            return cls.Output(error=f"Path doesn't exist: {path!r}", contents=None)
        if not path.is_file():
            logger.error(f"Path is not a file: {path!r}")
            return cls.Output(error=f"Path is not a file: {path!r}", contents=None)

        text = path.read_text()
        return cls.Output(contents=text, error=None)

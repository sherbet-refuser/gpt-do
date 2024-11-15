from __future__ import annotations

import logging
import subprocess as sp
from typing import Optional

from pydantic import BaseModel

from .action import Action

logger = logging.getLogger(__name__)


class ExecuteBashCommand(
    Action["ExecuteBashCommand.Args", "ExecuteBashCommand.Output"]
):
    """Execute an arbitrary Bash command.

    Args:
        command: The Bash command to execute.

    Output:
        stdout: The standard output.
        stderr: The standard error.
        return_code: The return code.
    """

    confirm = True

    class Args(BaseModel):
        command: str

    class Output(BaseModel):
        stdout: Optional[str]
        stderr: Optional[str]
        return_code: Optional[int]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the Bash command."""
        result = sp.run(
            args.command,
            shell=True,
            text=True,
            check=False,
            capture_output=True,
        )

        return cls.Output(
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode,
        )

from __future__ import annotations

import logging

from pydantic import BaseModel
from rich import print as rprint
from rich.markdown import Markdown

from .action import Action

logger = logging.getLogger(__name__)


class DisplayToUser(Action["DisplayToUser.Args", "DisplayToUser.Output"]):
    """Display a message to the user (no user response will be provided).

    Args:
        message: The message to display to the user.

    Output:
        displayed: A boolean indicating whether the message was displayed.
    """

    confirm = False

    class Args(BaseModel):
        message: str

    class Output(BaseModel):
        displayed: bool

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        # TODO: print helper
        msg = args.message.replace(r"\\\\", r"\\")
        # Console().print(md)
        rprint(Markdown(msg))
        return cls.Output(displayed=True)

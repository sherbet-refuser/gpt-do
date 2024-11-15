from __future__ import annotations

import datetime as dt

from pydantic import BaseModel

from .action import Action


class CheckDateTime(Action["CheckDateTime.Args", "CheckDateTime.Output"]):
    """Get the current date and time.

    Args:
        None

    Output:
        date_time: The current date and time.
    """

    confirm = False

    class Args(BaseModel):
        pass

    class Output(BaseModel):
        date_time: dt.datetime

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        date_time = dt.datetime.now()
        return cls.Output(date_time=date_time)

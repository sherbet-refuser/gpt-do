from __future__ import annotations

import datetime as dt
import subprocess as sp
from typing import Optional
from zoneinfo import ZoneInfo

from ics import Calendar, Event
from pydantic import BaseModel

from .. import TMP_DIR
from .action import Action


class AddToCalendar(Action["AddToCalendar.Args", "AddToCalendar.Output"]):
    """Create an event to add to the user's calendar.

    Args:
        name: The name of the event.
        begin: The start time of the event as an ISO 8601 string.
            Use Pacific Time (America/Los_Angeles).
            Leave empty if all-day event.
        duration: The duration of the event.
            Leave empty if all-day event.
        location: The location of the event.
            If the event is online, indicate that in this field.
        description: A description of the event.
        url: A URL associated with the event.

    Output:
        success: Whether the event was successfully added to the calendar.
    """

    confirm = True

    class Duration(BaseModel):
        hours: int
        minutes: int

    class Args(BaseModel):
        name: str
        begin: Optional[str]
        duration: Optional[AddToCalendar.Duration]
        location: Optional[str]
        description: Optional[str]
        url: Optional[str]

    class Output(BaseModel):
        success: bool

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        begin = (
            dt.datetime.fromisoformat(args.begin).replace(
                tzinfo=ZoneInfo("America/Los_Angeles")
            )
            if args.begin is not None
            else None
        )
        duration = (
            dt.timedelta(
                hours=args.duration.hours,
                minutes=args.duration.minutes,
            )
            if args.duration is not None
            else None
        )
        event = Event(
            name=args.name,
            begin=begin,
            duration=duration,
            location=args.location,
            description=args.description,
            url=args.url,
        )
        cal = Calendar(events=[event])
        ics_path = TMP_DIR / "event.ics"
        with ics_path.open("w") as f:
            f.writelines(cal)

        sp.check_call(["open", ics_path])
        if cls.confirm:
            input("Press Enter to continue...")
            print()

        return cls.Output(success=True)

from __future__ import annotations

import logging
from typing import Optional

import requests
from pydantic import BaseModel

from .action import Action

logger = logging.getLogger(__name__)


class CheckLocation(Action["CheckLocation.Args", "CheckLocation.Output"]):
    """Get the user's location, based on IP.

    Args:
        None

    Output:
        city: The user's city.
        region: The user's region.
        country: The user's country.
        error: An error message if the location could not be determined.
    """

    confirm = True

    class Args(BaseModel):
        pass

    class Output(BaseModel):
        city: Optional[str]
        region: Optional[str]
        country: Optional[str]
        error: Optional[str]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        try:
            response = requests.get("http://ipinfo.io", timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.exception("Failed to load web page")
            return cls.Output(error=str(e), city=None, region=None, country=None)
        data = response.json()
        return cls.Output(
            city=data.get("city"),
            region=data.get("region"),
            country=data.get("country"),
            error=None,
        )

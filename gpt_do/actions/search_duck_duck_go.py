from __future__ import annotations

import logging
from typing import Optional

import requests
from pydantic import BaseModel

from .action import Action

logger = logging.getLogger(__name__)

TIMEOUT_S = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.102 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
}


class SearchDuckDuckGo(Action["SearchDuckDuckGo.Args", "SearchDuckDuckGo.Output"]):
    """Search DuckDuckGo Instant Answer API for a query.

    Args:
        query: The search term.

    Output:
        answer: The Instant Answer text from DuckDuckGo.
        error: An error message if the answer could not be retrieved.
    """

    confirm = True

    class Args(BaseModel):
        query: str

    class Output(BaseModel):
        answer: Optional[str]
        error: Optional[str]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the DuckDuckGo search action."""
        url = "https://api.duckduckgo.com/"
        params: dict[str, str | int] = {
            "q": args.query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=TIMEOUT_S,
                headers=HEADERS,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.exception("Failed to retrieve DuckDuckGo Instant Answer")
            return cls.Output(answer=None, error=str(e))

        answer = data.get("AbstractText")
        if not answer:
            return cls.Output(
                answer=None, error="No Instant Answer found for this query."
            )
        return cls.Output(answer=answer, error=None)

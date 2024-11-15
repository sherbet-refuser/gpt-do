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


class SearchWikipedia(Action["SearchWikipedia.Args", "SearchWikipedia.Output"]):
    """Search Wikipedia and retrieve the introductory extract of an article.

    Args:
        query: The search term or article title.

    Output:
        content: The introductory extract of the Wikipedia page.
        error: An error message if the content could not be retrieved.
    """

    confirm = True

    class Args(BaseModel):
        query: str

    class Output(BaseModel):
        content: Optional[str]
        error: Optional[str]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the Wikipedia search action."""
        url = "https://en.wikipedia.org/w/api.php"
        params: dict[str, str | bool | int] = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "redirects": 1,
            "titles": args.query,
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
            logger.exception("Failed to retrieve Wikipedia content")
            return cls.Output(content=None, error=str(e))

        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return cls.Output(content=None, error="No pages found.")

        page = next(iter(pages.values()))
        extract = page.get("extract")
        if not extract:
            return cls.Output(content=None, error="No extract available for this page.")

        return cls.Output(content=extract, error=None)

from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
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
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class LoadWebPage(Action["LoadWebPage.Args", "LoadWebPage.Output"]):
    """Load a web page given a URL.

    If you don't know the exact URL, you can start from the home page
    and follow links to the desired page.

    Args:
        url: The URL of the web page.

    Output:
        text: The text content of the web page.
        links: A list of URLs found in the web page.
        error: An error message if the page could not be loaded.
    """

    confirm = True

    class Args(BaseModel):
        url: str

    class Output(BaseModel):
        text: Optional[str]
        links: Optional[list[str]]
        error: Optional[str]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        try:
            response = requests.get(
                args.url,
                timeout=TIMEOUT_S,
                allow_redirects=True,
                headers=HEADERS,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.exception("Failed to load web page")
            return cls.Output(error=str(e), text=None, links=None)

        # Ensure correct encoding
        if response.encoding is None:
            response.encoding = response.apparent_encoding

        response_text = response.text

        soup = BeautifulSoup(response_text, "lxml")

        # Extract text
        # text = soup.get_text(separator="\n", strip=True)
        text = "\n".join(text for text in soup.stripped_strings if text)

        # Extract links
        base_url = response.url  # The final URL after redirects
        links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)
            links.append(full_url)
        # deduplicate links while preserving order
        links = list(dict.fromkeys(links))

        return cls.Output(text=text, links=links, error=None)

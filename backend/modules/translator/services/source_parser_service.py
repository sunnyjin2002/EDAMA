"""News source clients — abstract interface + HTML scraper implementation.

The :class:`NewsSourceClient` interface lets us swap the underlying data
source without touching the polling/ingestion layer.  Currently only the
community-site HTML scraper is implemented; a JSON API client can be added
later by implementing the same interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class NewsArticle:
    """Normalised article returned by any news source client."""

    uid: str
    title: str
    url: str
    body: str
    published_at: datetime | None


class NewsSourceClient(ABC):
    """Abstract interface for fetching Galnet-style news articles.

    Implementations must return a list of :class:`NewsArticle` where each
    item has a stable ``uid`` used for deduplication against the database.
    """

    @abstractmethod
    async def fetch_articles(self) -> list[NewsArticle]:
        """Fetch the latest articles from the configured source."""

    async def aclose(self) -> None:
        """Close resources held by the client, if any."""


class CommunitySiteClient(NewsSourceClient):
    """Scrapes articles from the official Elite Dangerous community site."""

    base_url = "https://community.elitedangerous.com"
    list_path = "/galnet"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; EDAMA/0.1)"},
        )

    async def fetch_articles(self) -> list[NewsArticle]:
        """Fetch the Galnet listing and full text of each article."""
        list_html = await self._get(self.list_path)
        links = self._parse_listing(list_html)

        articles: list[NewsArticle] = []
        for uid, title, url in links:
            detail_html = await self._get(f"/galnet/uid/{uid}")
            body, published_at = self._parse_detail(detail_html)
            articles.append(
                NewsArticle(
                    uid=uid,
                    title=title,
                    url=url,
                    body=body,
                    published_at=published_at,
                )
            )
        return articles

    async def _get(self, path: str) -> str:
        response = await self._client.get(f"{self.base_url}{path}")
        response.raise_for_status()
        return response.text

    async def aclose(self) -> None:
        """Close the underlying HTTP client when this class owns it."""
        if self._owns_client:
            await self._client.aclose()

    def _parse_listing(self, html: str) -> list[tuple[str, str, str]]:
        """Extract (uid, title, url) tuples from the listing page."""
        soup = BeautifulSoup(html, "html.parser")
        results: list[tuple[str, str, str]] = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/galnet/uid/" not in href:
                continue
            uid = href.rsplit("/", 1)[-1]
            title = link.get_text(strip=True)
            if not title:
                continue
            url = f"{self.base_url}{href}" if href.startswith("/") else href
            if not any(existing[0] == uid for existing in results):
                results.append((uid, title, url))
        return results

    def _parse_detail(self, html: str) -> tuple[str, datetime | None]:
        """Extract body text and publication date from a detail page."""
        soup = BeautifulSoup(html, "html.parser")
        paragraphs: list[str] = []
        for item in soup.select("div.article p:not(.small)"):
            text = item.get_text(strip=True)
            if text:
                paragraphs.append(text)
        body = "\n\n".join(paragraphs)

        published_at: datetime | None = None
        date_tag = soup.select_one("div.article p.small")
        if date_tag is not None:
            raw = date_tag.get_text(strip=True)
            try:
                published_at = datetime.strptime(raw, "%d %b %Y")
            except ValueError:
                published_at = None
        return body, published_at


def create_news_client(source_type: str) -> NewsSourceClient:
    """Return a news source client for the configured source type."""
    if source_type == "community":
        return CommunitySiteClient()
    # Future: add "api" source type with a JSON API client.
    raise ValueError(f"Unknown news source type: {source_type}")

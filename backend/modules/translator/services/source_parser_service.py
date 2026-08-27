"""News source clients - API first, community scraper fallback."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class NewsArticle:
    """Normalised article returned by a news source."""

    uid: str
    title: str
    url: str
    body: str
    published_at: datetime | None
    source_type: str = "galnet"
    legacy_uid: str | None = None


class NewsSourceClient(ABC):
    """Abstract interface for fetching Galnet or Community Goal articles."""

    @abstractmethod
    async def fetch_articles(self) -> list[NewsArticle]:
        """Fetch the latest articles from the configured source."""

    async def aclose(self) -> None:
        """Close resources held by the client, if any."""


def parse_elite_date(raw: str | None) -> datetime | None:
    """Parse an Elite-style or ISO date into a naive UTC datetime."""
    if not raw:
        return None
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    for fmt in ("%d %b %Y", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, fmt)
            if parsed.tzinfo is not None:
                parsed = parsed.replace(tzinfo=None)
            return parsed
        except ValueError:
            continue
    return None


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
                    source_type="galnet",
                    legacy_uid=uid,
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
            published_at = parse_elite_date(raw)
        return body, published_at


class GalnetApiClient(NewsSourceClient):
    """Reads Galnet articles from the JSON:API endpoint."""

    base_url = "https://cms.zaonce.net/en-GB/jsonapi/node/galnet_article"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; EDAMA/0.1)", "Accept": "application/vnd.api+json"},
        )

    async def fetch_articles(self) -> list[NewsArticle]:
        """Fetch the latest Galnet JSON:API page and normalize it."""
        data = await self._get_json(self.base_url)
        articles: list[NewsArticle] = []
        for item in data.get("data", []):
            attrs = item.get("attributes", {})
            uid = attrs.get("field_galnet_guid") or item.get("id")
            title = attrs.get("title") or "Untitled GalNet Article"
            body_value = attrs.get("body") or {}
            body = body_value.get("value") or body_value.get("processed") or ""
            url = (
                item.get("links", {}).get("self", {}).get("href")
                or f"{self.base_url}/{item.get('id')}"
            )
            published_at = parse_elite_date(attrs.get("field_galnet_date")) or parse_elite_date(attrs.get("published_at"))
            articles.append(
                NewsArticle(
                    uid=uid,
                    title=title,
                    url=url,
                    body=body,
                    published_at=published_at,
                    source_type="galnet",
                )
            )
        return articles

    async def _get_json(self, url: str) -> dict:
        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()


class CommunityGoalClient(NewsSourceClient):
    """Reads Community Goal initiatives from the Orerve API."""

    base_url = "https://api.orerve.net/2.0/website/initiatives/list?lang=en"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; EDAMA/0.1)", "Accept": "application/json"},
        )

    async def fetch_articles(self) -> list[NewsArticle]:
        """Fetch active Community Goals and normalize them defensively."""
        data = await self._get_json(self.base_url)
        active = data.get("activeInitiatives") or []
        articles: list[NewsArticle] = []
        for item in active:
            if not isinstance(item, dict):
                continue
            uid = (
                item.get("id")
                or item.get("initiativeId")
                or item.get("guid")
                or item.get("url")
            )
            title = item.get("title") or item.get("name") or "Community Goal"
            body = item.get("description") or item.get("summary") or ""
            url = item.get("url") or item.get("link") or self.base_url
            date_raw = item.get("endDate") or item.get("startDate") or item.get("date")
            published_at = parse_elite_date(str(date_raw) if date_raw else None)
            if not uid:
                uid = f"cg-{title}"
            articles.append(
                NewsArticle(
                    uid=str(uid),
                    title=title,
                    url=url,
                    body=body,
                    published_at=published_at,
                    source_type="community_goal",
                )
            )
        return articles

    async def _get_json(self, url: str) -> dict:
        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()


def create_news_client(source_type: str) -> NewsSourceClient:
    """Return a news source client for the configured source type."""
    if source_type == "galnet_api":
        return GalnetApiClient()
    if source_type == "community":
        return CommunitySiteClient()
    if source_type == "community_goal":
        return CommunityGoalClient()
    raise ValueError(f"Unknown news source type: {source_type}")

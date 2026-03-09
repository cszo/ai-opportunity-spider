from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import httpx

from config import AI_KEYWORDS
from src.models import RawItem

logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    """Base class for all data-source spiders."""

    source_name: str = "unknown"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            },
        )

    async def close(self) -> None:
        await self.client.aclose()

    @abstractmethod
    async def crawl(self) -> list[RawItem]:
        """Fetch and return raw items from the data source."""
        ...

    def filter_ai_items(self, items: list[RawItem]) -> list[RawItem]:
        """Keep only items whose title or description matches AI keywords."""
        result: list[RawItem] = []
        for item in items:
            text = f"{item.title} {item.description}".lower()
            if any(kw in text for kw in AI_KEYWORDS):
                result.append(item)
        return result

    async def run(self) -> list[RawItem]:
        """Crawl, filter, and return AI-related items."""
        try:
            raw = await self.crawl()
            filtered = self.filter_ai_items(raw)
            logger.info(
                "%s: crawled %d items, %d AI-related",
                self.source_name,
                len(raw),
                len(filtered),
            )
            return filtered
        except Exception:
            logger.exception("Spider %s failed", self.source_name)
            return []
        finally:
            await self.close()

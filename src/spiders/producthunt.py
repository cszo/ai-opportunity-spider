from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

from bs4 import BeautifulSoup, Tag

from src.models import RawItem
from src.spiders.base import BaseSpider

PH_BASE = "https://www.producthunt.com"


class ProductHuntSpider(BaseSpider):
    source_name = "producthunt"

    async def crawl(self) -> list[RawItem]:
        today = datetime.now(timezone(timedelta(hours=8))).date()
        url = f"{PH_BASE}/leaderboard/daily/{today.year}/{today.month}/{today.day}"
        resp = await self.client.get(url)
        resp.raise_for_status()
        return self._parse(resp.text)

    def _parse(self, html: str) -> list[RawItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[RawItem] = []

        for section in soup.select('section[data-test^="post-item-"]'):
            post_id = (section.get("data-test") or "").replace("post-item-", "")

            name_el = section.select_one(f'span[data-test="post-name-{post_id}"]')
            name = name_el.get_text(strip=True) if name_el else ""
            if not name:
                continue

            prod_link = section.select_one('a[href*="/products/"]')
            href = prod_link.get("href", "") if prod_link else ""
            url = f"{PH_BASE}{href}" if href else PH_BASE

            tagline = self._extract_tagline(section, name)

            vote_btn = section.select_one('button[data-test="vote-button"]')
            upvotes = self._parse_votes(vote_btn.get_text(strip=True)) if vote_btn else 0

            items.append(
                RawItem(
                    title=name,
                    url=url,
                    source="producthunt",
                    description=tagline,
                    metrics={"upvotes": upvotes, "ph_id": post_id},
                )
            )

        return items

    @staticmethod
    def _extract_tagline(section: Tag, name: str) -> str:
        """Extract the tagline from the section text (appears after the product name)."""
        full_text = section.get_text(" | ", strip=True)
        parts = full_text.split(" | ")
        # Tagline is typically the second segment after the product name
        for i, part in enumerate(parts):
            if part.strip() == name.strip() and i + 1 < len(parts):
                return parts[i + 1].strip()
        return ""

    @staticmethod
    def _parse_votes(text: str) -> int:
        digits = re.sub(r"[^\d]", "", text)
        return int(digits) if digits else 0

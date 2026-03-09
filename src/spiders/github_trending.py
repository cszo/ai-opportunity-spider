from __future__ import annotations

from bs4 import BeautifulSoup

from config import GITHUB_TRENDING_URL
from src.models import RawItem
from src.spiders.base import BaseSpider


class GitHubTrendingSpider(BaseSpider):
    source_name = "github"

    async def crawl(self) -> list[RawItem]:
        resp = await self.client.get(GITHUB_TRENDING_URL)
        resp.raise_for_status()
        return self._parse(resp.text)

    def _parse(self, html: str) -> list[RawItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[RawItem] = []

        for article in soup.select("article.Box-row"):
            name_tag = article.select_one("h2 a")
            if not name_tag:
                continue

            repo_path = name_tag.get("href", "").strip().lstrip("/")
            title = repo_path
            url = f"https://github.com/{repo_path}"

            desc_tag = article.select_one("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            stars_total = 0
            stars_today = 0

            star_links = article.select("a.Link--muted")
            if star_links:
                stars_text = star_links[0].get_text(strip=True).replace(",", "")
                stars_total = self._parse_number(stars_text)

            today_tag = article.select_one("span.d-inline-block.float-sm-right")
            if today_tag:
                today_text = today_tag.get_text(strip=True).replace(",", "")
                stars_today = self._parse_number(today_text)

            language = ""
            lang_tag = article.select_one("[itemprop='programmingLanguage']")
            if lang_tag:
                language = lang_tag.get_text(strip=True)

            items.append(
                RawItem(
                    title=title,
                    url=url,
                    source="github",
                    description=description,
                    metrics={
                        "stars_total": stars_total,
                        "stars_today": stars_today,
                        "language": language,
                    },
                )
            )

        return items

    @staticmethod
    def _parse_number(text: str) -> int:
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else 0

from __future__ import annotations

import asyncio

from config import HN_TOP_STORIES_LIMIT
from src.models import RawItem
from src.spiders.base import BaseSpider

HN_API = "https://hacker-news.firebaseio.com/v0"


class HackerNewsSpider(BaseSpider):
    source_name = "hackernews"

    async def crawl(self) -> list[RawItem]:
        resp = await self.client.get(f"{HN_API}/topstories.json")
        resp.raise_for_status()
        story_ids: list[int] = resp.json()[:HN_TOP_STORIES_LIMIT]

        tasks = [self._fetch_story(sid) for sid in story_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        items: list[RawItem] = []
        for r in results:
            if isinstance(r, RawItem):
                items.append(r)
        return items

    async def _fetch_story(self, story_id: int) -> RawItem:
        resp = await self.client.get(f"{HN_API}/item/{story_id}.json")
        resp.raise_for_status()
        data = resp.json()

        title = data.get("title", "")
        url = data.get("url", f"https://news.ycombinator.com/item?id={story_id}")
        score = data.get("score", 0)
        descendants = data.get("descendants", 0)

        return RawItem(
            title=title,
            url=url,
            source="hackernews",
            description=f"Score: {score} | Comments: {descendants}",
            metrics={
                "score": score,
                "comments": descendants,
                "hn_id": story_id,
            },
        )

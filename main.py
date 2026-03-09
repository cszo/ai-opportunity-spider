"""AI Opportunity Spider - Daily runner."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from src.analyzer import analyze_opportunities
from src.models import DailyReport
from src.reporter import generate_report
from src.spiders.github_trending import GitHubTrendingSpider
from src.spiders.hackernews import HackerNewsSpider
from src.spiders.producthunt import ProductHuntSpider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


async def run() -> str:
    logger.info("Starting AI Opportunity Spider")

    spiders = [
        GitHubTrendingSpider(),
        HackerNewsSpider(),
        ProductHuntSpider(),
    ]

    results = await asyncio.gather(*(s.run() for s in spiders))
    all_items = [item for batch in results for item in batch]
    logger.info("Total AI-related items collected: %d", len(all_items))

    if not all_items:
        logger.warning("No AI-related items found today, generating empty report")

    opportunities = await analyze_opportunities(all_items)

    today = datetime.now(timezone(timedelta(hours=8))).date()
    report = DailyReport(
        date=today,
        opportunities=opportunities,
        raw_items=all_items,
    )

    path = generate_report(report)
    logger.info("Report saved to %s", path)
    return path


def main() -> None:
    path = asyncio.run(run())
    print(f"\nDone! Report: {path}")


if __name__ == "__main__":
    main()

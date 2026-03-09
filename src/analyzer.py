from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from config import ZHIPU_API_KEY, ZHIPU_BASE_URL, ZHIPU_MODEL, TOP_OPPORTUNITIES_COUNT
from src.models import Opportunity, RawItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a senior AI industry analyst and startup advisor.

Your job: given today's crawled data from GitHub Trending, HackerNews, \
and ProductHunt, identify the strongest entrepreneurial signals.

Scoring dimensions:
- Growth velocity: abnormal star/vote/score growth in a short period
- Market gap: solves a problem nobody has solved well before
- Technical breakthrough: new method/architecture with significant improvement
- Community excitement: discussion volume, sentiment

Return a JSON object with this exact structure:
{
  "opportunities": [
    {
      "title": "short descriptive title of the opportunity",
      "signal_strength": <1-5 integer>,
      "source": "github / hackernews / producthunt / multiple",
      "why": "why this is a strong entrepreneurial signal (2-3 sentences)",
      "direction": "potential startup direction or product idea (1-2 sentences)",
      "category": "e.g. developer tools, AI infrastructure, consumer AI, etc.",
      "links": ["url1", "url2"]
    }
  ]
}

Rules:
- Return exactly TOP_N opportunities, ranked by signal strength (strongest first).
- Be specific and actionable; avoid vague statements.
- If the same trend appears across multiple sources, that amplifies the signal.
- Write in English.
""".replace("TOP_N", str(TOP_OPPORTUNITIES_COUNT))


async def analyze_opportunities(items: list[RawItem]) -> list[Opportunity]:
    """Send crawled items to Zhipu GLM and get back scored opportunities."""
    if not items:
        logger.warning("No items to analyze")
        return []

    client_kwargs: dict = {"api_key": ZHIPU_API_KEY}
    if ZHIPU_BASE_URL:
        client_kwargs["base_url"] = ZHIPU_BASE_URL
    client = AsyncOpenAI(**client_kwargs)

    items_text = _format_items(items)
    user_prompt = (
        f"Today's crawled data ({len(items)} AI-related items):\n\n"
        f"{items_text}\n\n"
        f"Identify the top {TOP_OPPORTUNITIES_COUNT} entrepreneurial opportunities."
    )

    try:
        response = await client.chat.completions.create(
            model=ZHIPU_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        raw_opportunities = data.get("opportunities", [])

        opportunities = [Opportunity(**opp) for opp in raw_opportunities]
        logger.info("AI identified %d opportunities", len(opportunities))
        return opportunities

    except Exception:
        logger.exception("Zhipu GLM analysis failed")
        return []


def _format_items(items: list[RawItem]) -> str:
    """Format items into a readable text block for the LLM."""
    lines: list[str] = []
    for i, item in enumerate(items, 1):
        metrics_str = ", ".join(f"{k}: {v}" for k, v in item.metrics.items())
        lines.append(
            f"{i}. [{item.source.upper()}] {item.title}\n"
            f"   URL: {item.url}\n"
            f"   Description: {item.description}\n"
            f"   Metrics: {metrics_str}"
        )
    return "\n\n".join(lines)

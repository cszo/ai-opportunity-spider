from __future__ import annotations

import os

from config import REPORTS_DIR
from src.models import DailyReport


def generate_report(report: DailyReport) -> str:
    """Generate a Markdown report and save it to disk. Returns the file path."""
    md = _render_markdown(report)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"{report.date.isoformat()}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return path


def _render_markdown(report: DailyReport) -> str:
    lines: list[str] = []

    lines.append(f"# AI Opportunity Radar - {report.date.isoformat()}\n")

    if not report.opportunities:
        lines.append("No significant opportunities identified today.\n")
        return "\n".join(lines)

    lines.append("## Top Opportunities\n")

    for i, opp in enumerate(report.opportunities, 1):
        stars = "\u2605" * opp.signal_strength + "\u2606" * (5 - opp.signal_strength)
        lines.append(f"### {i}. {opp.title}\n")
        lines.append(f"- **Signal Strength**: {stars}")
        lines.append(f"- **Source**: {opp.source}")
        if opp.category:
            lines.append(f"- **Category**: {opp.category}")
        lines.append(f"- **Why**: {opp.why}")
        lines.append(f"- **Direction**: {opp.direction}")
        if opp.links:
            links_md = ", ".join(f"[link]({url})" for url in opp.links)
            lines.append(f"- **Links**: {links_md}")
        lines.append("")

    lines.append("---\n")
    lines.append("## Today's Raw Data\n")

    stats = report.stats
    lines.append(f"| Source | AI-related Items |")
    lines.append(f"|--------|-----------------|")
    for source, count in sorted(stats.items()):
        label = {
            "github": "GitHub Trending",
            "hackernews": "HackerNews",
            "producthunt": "ProductHunt",
        }.get(source, source)
        lines.append(f"| {label} | {count} |")
    lines.append(f"| **Total** | **{sum(stats.values())}** |")
    lines.append("")

    return "\n".join(lines)

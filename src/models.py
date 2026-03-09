from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class RawItem(BaseModel):
    """A single item crawled from any data source."""

    title: str
    url: str
    source: str  # "github" | "hackernews" | "producthunt"
    description: str = ""
    metrics: dict[str, Any] = Field(default_factory=dict)


class Opportunity(BaseModel):
    """An entrepreneurial opportunity identified by AI analysis."""

    title: str
    signal_strength: int = Field(ge=1, le=5, description="1-5 star rating")
    source: str
    why: str
    direction: str
    category: str = ""
    links: list[str] = Field(default_factory=list)


class DailyReport(BaseModel):
    """The complete daily report."""

    date: date
    opportunities: list[Opportunity]
    raw_items: list[RawItem] = Field(default_factory=list)

    @property
    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.raw_items:
            counts[item.source] = counts.get(item.source, 0) + 1
        return counts

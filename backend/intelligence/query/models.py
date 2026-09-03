"""Query intent models. Keep these independent from any LLM SDK."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryIntent:
    intent: str
    entity: str | None = None
    depth: int | None = None

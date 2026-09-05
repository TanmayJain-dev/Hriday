"""Query models independent of any LLM SDK."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from backend.intelligence.graph.models import GraphResult

__all__ = ["QueryIntent", "Answer", "GraphResult"]


@dataclass(frozen=True)
class QueryIntent:
    """Query intent specification conforming to contracts/query.schema.json."""
    intent: str
    entity: str | None = None
    target_entity: str | None = None
    depth: int | None = None


@dataclass(frozen=True)
class Answer:
    """Query answer model conforming to contracts/answer.schema.json."""
    answer: str
    confidence: float
    graph_result: dict[str, Any] = field(default_factory=dict)
    evidence: list[Any] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=lambda: {"status": "not_required"})

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "graph_result": self.graph_result,
            "evidence": self.evidence,
            "verification": self.verification,
        }

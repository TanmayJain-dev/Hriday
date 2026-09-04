"""Query models independent of any LLM SDK."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class QueryIntent:
    intent: str
    entity: str | None = None
    depth: int | None = None

@dataclass(frozen=True)
class GraphResult:
    document_id: str
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "nodes": list(self.nodes),
            "edges": list(self.edges),
        }

@dataclass(frozen=True)
class Answer:
    answer: str
    confidence: float
    graph_result: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=lambda: {"status": "not_required"})

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "graph_result": self.graph_result,
            "evidence": self.evidence,
            "verification": self.verification,
        }

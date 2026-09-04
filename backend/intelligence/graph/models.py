"""Canonical graph domain models for the MVP."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GraphNode:
    """Canonical representation of an engineering entity in the P&ID graph."""
    id: str
    type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "confidence": self.confidence,
        }
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        if self.evidence_ids:
            result["evidence_ids"] = list(self.evidence_ids)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphNode:
        return cls(
            id=str(data["id"]),
            type=str(data.get("type", "unknown")),
            attributes=dict(data.get("attributes", {})),
            confidence=float(data.get("confidence", 1.0)),
            evidence_ids=tuple(data.get("evidence_ids", ())),
        )


@dataclass(frozen=True)
class GraphEdge:
    """Canonical representation of a directed relationship between two entities."""
    source: str
    target: str
    relationship: str = "CONNECTED_TO"
    attributes: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
            "confidence": self.confidence,
        }
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        if self.evidence_ids:
            result["evidence_ids"] = list(self.evidence_ids)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphEdge:
        return cls(
            source=str(data["source"]),
            target=str(data["target"]),
            relationship=str(data.get("relationship", "CONNECTED_TO")),
            attributes=dict(data.get("attributes", {})),
            confidence=float(data.get("confidence", 1.0)),
            evidence_ids=tuple(data.get("evidence_ids", ())),
        )


@dataclass(frozen=True)
class GraphPath:
    """A traversed path through the graph preserving confidence and provenance."""
    nodes: tuple[str, ...]
    edges: tuple[GraphEdge, ...] = ()
    confidence: float = 1.0
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.edges:
            min_edge_conf = min(e.confidence for e in self.edges)
            object.__setattr__(self, "confidence", round(min(self.confidence, min_edge_conf), 4))
        if self.edges and not self.evidence_ids:
            seen_evidence: list[str] = []
            for edge in self.edges:
                for eid in edge.evidence_ids:
                    if eid not in seen_evidence:
                        seen_evidence.append(eid)
            object.__setattr__(self, "evidence_ids", tuple(seen_evidence))

    def to_string(self) -> str:
        return " -> ".join(self.nodes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": list(self.nodes),
            "confidence": self.confidence,
            "evidence_ids": list(self.evidence_ids),
            "edge_count": len(self.edges),
        }


@dataclass(frozen=True)
class GraphResult:
    """Graph output conforming to contracts/graph.schema.json."""
    document_id: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "nodes": self.nodes,
            "edges": self.edges,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphResult:
        return cls(
            document_id=str(data["document_id"]),
            nodes=list(data.get("nodes", [])),
            edges=list(data.get("edges", [])),
        )

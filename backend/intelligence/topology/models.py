from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class TopologyNode:
    id: str
    type: str
    confidence: float
    attributes: dict[str, Any] = field(default_factory=dict)
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

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
    def from_dict(cls, data: dict[str, Any]) -> TopologyNode:
        return cls(
            id=str(data["id"]),
            type=str(data.get("type", "unknown")),
            confidence=float(data["confidence"]),
            attributes=dict(data.get("attributes", {})),
            evidence_ids=tuple(data.get("evidence_ids", ())),
        )

@dataclass(frozen=True)
class TopologyEdge:
    source: str
    target: str
    relationship: str = "CONNECTED_TO"
    confidence: float | None = None
    evidence_ids: tuple[str, ...] = ()
    requires_verification: bool = False
    reason: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.confidence is None:
            raise ValueError("TopologyEdge requires explicit confidence")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
            "confidence": self.confidence,
            "requires_verification": self.requires_verification,
        }
        if self.evidence_ids:
            result["evidence_ids"] = list(self.evidence_ids)
        if self.reason is not None:
            result["reason"] = self.reason
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TopologyEdge:
        return cls(
            source=str(data["source"]),
            target=str(data["target"]),
            relationship=str(data.get("relationship", "CONNECTED_TO")),
            confidence=float(data["confidence"]),
            evidence_ids=tuple(data.get("evidence_ids", ())),
            requires_verification=bool(data.get("requires_verification", False)),
            reason=data.get("reason"),
            attributes=dict(data.get("attributes", {})),
        )


@dataclass(frozen=True)
class TopologyResult:
    """Topology contract consumed by graph construction."""

    document_id: str
    nodes: tuple[TopologyNode, ...] = ()
    edges: tuple[TopologyEdge, ...] = ()
    uncertainties: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "uncertainties": [dict(uncertainty) for uncertainty in self.uncertainties],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TopologyResult:
        return cls(
            document_id=str(data["document_id"]),
            nodes=tuple(TopologyNode.from_dict(node) for node in data.get("nodes", ())),
            edges=tuple(TopologyEdge.from_dict(edge) for edge in data.get("edges", ())),
            uncertainties=tuple(dict(uncertainty) for uncertainty in data.get("uncertainties", ())),
        )

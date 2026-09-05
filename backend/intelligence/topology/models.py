from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Point:
        return cls(x=float(data["x"]), y=float(data["y"]))


@dataclass(frozen=True)
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def to_dict(self) -> dict[str, float]:
        return {
            "x_min": self.x_min,
            "y_min": self.y_min,
            "x_max": self.x_max,
            "y_max": self.y_max,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BoundingBox:
        return cls(
            x_min=float(data["x_min"]),
            y_min=float(data["y_min"]),
            x_max=float(data["x_max"]),
            y_max=float(data["y_max"]),
        )


def _confidence(value: Any) -> float:
    result = float(value)
    if not 0.0 <= result <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")
    return result


@dataclass(frozen=True)
class ComponentObservation:
    id: str
    type: str
    confidence: float
    tag: str | None = None
    bbox: BoundingBox | None = None
    connection_points: tuple[Point, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    evidence_references: tuple[dict[str, Any], ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", _confidence(self.confidence))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "confidence": self.confidence,
            "connection_points": [point.to_dict() for point in self.connection_points],
        }
        if self.tag is not None:
            result["tag"] = self.tag
        if self.bbox is not None:
            result["bbox"] = self.bbox.to_dict()
        if self.evidence_ids:
            result["evidence_ids"] = list(self.evidence_ids)
        if self.evidence_references:
            result["evidence_references"] = [dict(ref) for ref in self.evidence_references]
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ComponentObservation:
        return cls(
            id=str(data["id"]),
            type=str(data.get("type", "unknown")),
            confidence=_confidence(data["confidence"]),
            tag=data.get("tag"),
            bbox=BoundingBox.from_dict(data["bbox"]) if data.get("bbox") else None,
            connection_points=tuple(
                Point.from_dict(point) for point in data.get("connection_points", ())
            ),
            evidence_ids=tuple(data.get("evidence_ids", ())),
            evidence_references=tuple(
                dict(ref) for ref in data.get("evidence_references", ())
            ),
            attributes=dict(data.get("attributes", {})),
        )


@dataclass(frozen=True)
class LineCandidate:
    line_id: str
    start: Point
    end: Point
    confidence: float
    bbox: BoundingBox | None = None
    points: tuple[Point, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    evidence_references: tuple[dict[str, Any], ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", _confidence(self.confidence))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "line_id": self.line_id,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "confidence": self.confidence,
        }
        if self.bbox is not None:
            result["bbox"] = self.bbox.to_dict()
        if self.points:
            result["points"] = [point.to_dict() for point in self.points]
        if self.evidence_ids:
            result["evidence_ids"] = list(self.evidence_ids)
        if self.evidence_references:
            result["evidence_references"] = [dict(ref) for ref in self.evidence_references]
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LineCandidate:
        return cls(
            line_id=str(data["line_id"]),
            start=Point.from_dict(data["start"]),
            end=Point.from_dict(data["end"]),
            confidence=_confidence(data["confidence"]),
            bbox=BoundingBox.from_dict(data["bbox"]) if data.get("bbox") else None,
            points=tuple(Point.from_dict(point) for point in data.get("points", ())),
            evidence_ids=tuple(data.get("evidence_ids", ())),
            evidence_references=tuple(
                dict(ref) for ref in data.get("evidence_references", ())
            ),
            attributes=dict(data.get("attributes", {})),
        )


@dataclass(frozen=True)
class JunctionCandidate:
    junction_id: str
    point: Point
    confidence: float
    evidence_ids: tuple[str, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", _confidence(self.confidence))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "junction_id": self.junction_id,
            "point": self.point.to_dict(),
            "confidence": self.confidence,
        }
        if self.evidence_ids:
            result["evidence_ids"] = list(self.evidence_ids)
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JunctionCandidate:
        return cls(
            junction_id=str(data["junction_id"]),
            point=Point.from_dict(data["point"]),
            confidence=_confidence(data["confidence"]),
            evidence_ids=tuple(data.get("evidence_ids", ())),
            attributes=dict(data.get("attributes", {})),
        )


@dataclass(frozen=True)
class ExtractionResult:
    """Observation contract; it does not assert process connectivity."""

    document_id: str
    entities: tuple[ComponentObservation, ...] = ()
    text_regions: tuple[dict[str, Any], ...] = ()
    line_candidates: tuple[LineCandidate, ...] = ()
    junction_candidates: tuple[JunctionCandidate, ...] = ()
    uncertainties: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "entities": [entity.to_dict() for entity in self.entities],
            "text_regions": [dict(region) for region in self.text_regions],
            "line_candidates": [line.to_dict() for line in self.line_candidates],
            "junction_candidates": [junction.to_dict() for junction in self.junction_candidates],
            "uncertainties": [dict(uncertainty) for uncertainty in self.uncertainties],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExtractionResult:
        return cls(
            document_id=str(data["document_id"]),
            entities=tuple(ComponentObservation.from_dict(entity) for entity in data.get("entities", ())),
            text_regions=tuple(dict(region) for region in data.get("text_regions", ())),
            line_candidates=tuple(
                LineCandidate.from_dict(line) for line in data.get("line_candidates", ())
            ),
            junction_candidates=tuple(
                JunctionCandidate.from_dict(junction)
                for junction in data.get("junction_candidates", ())
            ),
            uncertainties=tuple(dict(uncertainty) for uncertainty in data.get("uncertainties", ())),
        )

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

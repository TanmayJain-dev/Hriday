from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BoundingBox:
    """Axis-aligned bounding box in page coordinates."""

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


@dataclass
class TextRegion:
    """Observable text detected on a document page."""

    text: str
    page: int
    bbox: BoundingBox
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "page": self.page,
            "bbox": self.bbox.to_dict(),
            "confidence": self.confidence,
        }


@dataclass
class EntityObservation:
    """Visual entity observed in a document."""

    entity_id: str
    entity_type: str
    page: int
    bbox: BoundingBox
    confidence: float
    tag: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.entity_id,
            "type": self.entity_type,
            "page": self.page,
            "bbox": self.bbox.to_dict(),
            "confidence": self.confidence,
            "tag": self.tag,
        }


@dataclass
class LineCandidate:
    """Candidate process/instrument line detected visually.

    This is only a visual observation. It does not establish
    final connectivity between entities.
    """

    line_id: str
    page: int
    geometry: list[dict[str, float]]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.line_id,
            "page": self.page,
            "geometry": self.geometry,
            "confidence": self.confidence,
        }


@dataclass
class Uncertainty:
    """Something the extraction pipeline could not determine reliably."""

    uncertainty_type: str
    message: str
    page: int | None = None
    confidence: float | None = None
    related_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.uncertainty_type,
            "message": self.message,
            "page": self.page,
            "confidence": self.confidence,
            "related_ids": self.related_ids,
        }


@dataclass
class ExtractionResult:
    """Contract-level output produced by visual extraction."""

    document_id: str
    entities: list[EntityObservation] = field(default_factory=list)
    text_regions: list[TextRegion] = field(default_factory=list)
    line_candidates: list[LineCandidate] = field(default_factory=list)
    uncertainties: list[Uncertainty] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "entities": [entity.to_dict() for entity in self.entities],
            "text_regions": [
                region.to_dict() for region in self.text_regions
            ],
            "line_candidates": [
                line.to_dict() for line in self.line_candidates
            ],
            "uncertainties": [
                uncertainty.to_dict()
                for uncertainty in self.uncertainties
            ],
        }
"""Evidence domain models."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceReference:
    document_id: str
    page: int
    bbox: tuple[float, float, float, float]
    source_type: str = "diagram"
    confidence: float = 1.0

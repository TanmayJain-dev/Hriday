"""Canonical graph domain models for the MVP."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relationship: str
    attributes: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    evidence_ids: tuple[str, ...] = ()

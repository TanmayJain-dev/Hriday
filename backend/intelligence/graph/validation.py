"""Graph-level validation hooks."""
from __future__ import annotations

from .interfaces import GraphEdge


def validate_edge(edge: GraphEdge) -> list[str]:
    errors: list[str] = []
    if not edge.source or not edge.target:
        errors.append("missing_endpoint")
    if not 0.0 <= edge.confidence <= 1.0:
        errors.append("confidence_out_of_range")
    if not edge.evidence_ids:
        errors.append("missing_provenance")
    return errors

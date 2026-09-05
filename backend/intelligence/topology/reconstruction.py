"""Orchestration for complete deterministic topology reconstruction."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Any

from backend.intelligence.extraction.models import ExtractionResult

from .connectivity import EndpointMatchingConfig, reconstruct_endpoint_connectivity
from .crossings import (
    CrossingClassificationConfig,
    reconstruct_with_crossing_classification,
)
from .models import TopologyEdge, TopologyNode, TopologyResult


@dataclass(frozen=True)
class TopologyReconstructionConfig:
    """Explicit engineering tolerances for each deterministic topology stage.

    These are domain matching tolerances, distinct from the numerical geometry
    tolerance. Topology reconstruction never infers process direction or
    operational intent.
    """

    endpoint_tolerance: float
    junction_tolerance: float
    intersection_tolerance: float

    def __post_init__(self) -> None:
        for name, value in (
            ("endpoint_tolerance", self.endpoint_tolerance),
            ("junction_tolerance", self.junction_tolerance),
            ("intersection_tolerance", self.intersection_tolerance),
        ):
            if value < 0.0 or not math.isfinite(value):
                raise ValueError(f"{name} must be finite and non-negative")


class DeterministicTopologyReconstructor:
    """TopologyProvider for the complete deterministic reconstruction pipeline."""

    def __init__(self, config: TopologyReconstructionConfig) -> None:
        self.config = config

    def reconstruct(self, extraction_result: ExtractionResult) -> TopologyResult:
        return reconstruct_topology(extraction_result, self.config)


def reconstruct_topology(
    extraction_result: ExtractionResult,
    config: TopologyReconstructionConfig,
) -> TopologyResult:
    """Convert an ExtractionResult into a conservative TopologyResult.

    The pipeline establishes physical connectivity from visual observations
    and deterministic geometric/domain rules. It does not infer process flow
    direction, operational intent, or component-to-component shortcuts.
    """
    _validate_extraction_ids(extraction_result)
    endpoint_result = reconstruct_endpoint_connectivity(
        extraction_result,
        EndpointMatchingConfig(config.endpoint_tolerance),
    )
    junction_result = reconstruct_with_crossing_classification(
        extraction_result,
        CrossingClassificationConfig(config.intersection_tolerance),
        junction_tolerance=config.junction_tolerance,
    )
    merged_nodes = _merge_nodes(endpoint_result.nodes, junction_result.nodes)
    merged_edges, edge_uncertainties = _merge_edges(
        endpoint_result.edges,
        junction_result.edges,
    )
    merged_uncertainties = _merge_uncertainties(
        extraction_result.uncertainties,
        endpoint_result.uncertainties,
        junction_result.uncertainties,
        edge_uncertainties,
    )
    return TopologyResult(
        document_id=extraction_result.document_id,
        nodes=merged_nodes,
        edges=merged_edges,
        uncertainties=merged_uncertainties,
    )


def _validate_extraction_ids(extraction_result: ExtractionResult) -> None:
    if not extraction_result.document_id.strip():
        raise ValueError("document_id must be non-empty")

    identifiers: list[tuple[str, str]] = []
    identifiers.extend(("component", entity.id) for entity in extraction_result.entities)
    identifiers.extend(("line", line.line_id) for line in extraction_result.line_candidates)
    identifiers.extend(
        ("junction", candidate.junction_id)
        for candidate in extraction_result.junction_candidates
    )
    seen: set[str] = set()
    for kind, identifier in identifiers:
        if not identifier.strip():
            raise ValueError(f"{kind} ID must be non-empty")
        if identifier in seen:
            raise ValueError(f"duplicate topology input ID: {identifier}")
        seen.add(identifier)


def _merge_nodes(*groups: tuple[TopologyNode, ...]) -> tuple[TopologyNode, ...]:
    by_id: dict[str, TopologyNode] = {}
    for group in groups:
        for node in group:
            existing = by_id.get(node.id)
            by_id[node.id] = node if existing is None else _merge_node(existing, node)
    return tuple(sorted(by_id.values(), key=lambda node: node.id))


def _merge_node(first: TopologyNode, second: TopologyNode) -> TopologyNode:
    attributes = dict(first.attributes)
    for key, value in second.attributes.items():
        if key not in attributes:
            attributes[key] = value
    return TopologyNode(
        id=first.id,
        type=first.type,
        confidence=min(first.confidence, second.confidence),
        attributes=attributes,
        evidence_ids=_merge_ids(first.evidence_ids, second.evidence_ids),
    )


def _merge_edges(
    *groups: tuple[TopologyEdge, ...],
) -> tuple[tuple[TopologyEdge, ...], tuple[dict[str, Any], ...]]:
    by_key: dict[tuple[str, str, str], TopologyEdge] = {}
    for group in groups:
        for edge in group:
            key = (edge.source, edge.target, edge.relationship)
            existing = by_key.get(key)
            by_key[key] = edge if existing is None else _merge_edge(existing, edge)
    merged_edges = tuple(
        sorted(
            by_key.values(),
            key=lambda edge: (edge.source, edge.target, edge.relationship),
        )
    )
    valid_edges = tuple(edge for edge in merged_edges if edge.evidence_ids)
    missing_provenance = tuple(
        {
            "source": edge.source,
            "target": edge.target,
            "relationship": edge.relationship,
            "confidence": edge.confidence,
            "reason": "missing_provenance",
            "requires_verification": True,
            "evidence_ids": [],
        }
        for edge in merged_edges
        if not edge.evidence_ids
    )
    return valid_edges, missing_provenance


def _merge_edge(first: TopologyEdge, second: TopologyEdge) -> TopologyEdge:
    attributes = dict(first.attributes)
    for key, value in second.attributes.items():
        if key not in attributes:
            attributes[key] = value
    return TopologyEdge(
        source=first.source,
        target=first.target,
        relationship=first.relationship,
        confidence=min(first.confidence, second.confidence),
        evidence_ids=_merge_ids(first.evidence_ids, second.evidence_ids),
        requires_verification=first.requires_verification or second.requires_verification,
        reason=first.reason or second.reason,
        attributes=attributes,
    )


def _merge_uncertainties(
    *groups: tuple[dict[str, Any], ...] | list[dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    by_key: dict[str, dict[str, Any]] = {}
    for group in groups:
        for uncertainty in group:
            record = dict(uncertainty)
            key = _uncertainty_key(record)
            existing = by_key.get(key)
            by_key[key] = record if existing is None else _merge_uncertainty(existing, record)
    return tuple(by_key[key] for key in sorted(by_key))


def _uncertainty_key(record: dict[str, Any]) -> str:
    identity = {
        key: record[key]
        for key in (
            "reason",
            "source",
            "target",
            "line_id",
            "line_ids",
            "line_endpoint",
            "point",
            "kind",
            "candidate_component_ids",
        )
        if key in record
    }
    return json.dumps(identity, sort_keys=True, separators=(",", ":"))


def _merge_uncertainty(
    first: dict[str, Any],
    second: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(first)
    merged["evidence_ids"] = list(
        _merge_ids(tuple(first.get("evidence_ids", ())), tuple(second.get("evidence_ids", ())))
    )
    merged["requires_verification"] = bool(
        first.get("requires_verification", False)
        or second.get("requires_verification", False)
    )
    if "confidence" in first and "confidence" in second:
        merged["confidence"] = min(float(first["confidence"]), float(second["confidence"]))
    for key, value in second.items():
        merged.setdefault(key, value)
    return merged


def _merge_ids(*groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for group in groups:
        for evidence_id in group:
            if evidence_id not in merged:
                merged.append(evidence_id)
    return tuple(merged)
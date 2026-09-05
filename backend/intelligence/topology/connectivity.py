"""Deterministic component-to-line endpoint connectivity."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from .models import ExtractionResult

from .geometry import distance, points_close
from .models import TopologyEdge, TopologyNode, TopologyResult


@dataclass(frozen=True)
class EndpointMatchingConfig:
    """Configuration for topology matching, separate from numerical tolerance."""

    endpoint_tolerance: float

    def __post_init__(self) -> None:
        if self.endpoint_tolerance < 0.0 or not math.isfinite(self.endpoint_tolerance):
            raise ValueError("endpoint_tolerance must be finite and non-negative")


@dataclass(frozen=True)
class EndpointMatch:
    component_id: str
    line_id: str
    component_point_index: int
    line_endpoint: str
    distance: float


def reconstruct_endpoint_connectivity(
    extraction_result: ExtractionResult,
    config: EndpointMatchingConfig,
) -> TopologyResult:
    """Build component-to-line endpoint relationships from observations.

    A component connection point matches a line endpoint only when their
    Euclidean distance is within ``config.endpoint_tolerance``. Matches are
    geometric facts only: neither endpoint is interpreted as upstream or
    downstream. If multiple components compete for one line endpoint, all
    competing relationships are routed to ``uncertainties`` instead of being
    asserted as topology edges.
    """
    nodes = _build_nodes(extraction_result)
    matches = _deduplicate_matches(_find_matches(extraction_result, config))
    ambiguous_keys = _ambiguous_endpoint_keys(matches)
    edges: list[TopologyEdge] = []
    uncertainties: list[dict[str, Any]] = []

    for match in matches:
        key = (match.line_id, match.line_endpoint)
        if key in ambiguous_keys:
            continue
        component = _component_by_id(extraction_result, match.component_id)
        line = _line_by_id(extraction_result, match.line_id)
        evidence_ids = _merge_evidence_ids(component.evidence_ids, line.evidence_ids)
        edges.append(
            TopologyEdge(
                source=match.component_id,
                target=match.line_id,
                relationship="CONNECTED_TO",
                confidence=min(component.confidence, line.confidence),
                evidence_ids=evidence_ids,
                attributes={
                    "line_endpoint": match.line_endpoint,
                    "component_point_index": match.component_point_index,
                    "endpoint_distance": match.distance,
                },
            )
        )

    for line_id, endpoint in sorted(ambiguous_keys):
        candidates = [
            match for match in matches
            if match.line_id == line_id and match.line_endpoint == endpoint
        ]
        uncertainties.append(
            {
                "line_id": line_id,
                "line_endpoint": endpoint,
                "candidate_component_ids": sorted(
                    {match.component_id for match in candidates}
                ),
                "reason": "multiple_components_match_line_endpoint",
                "requires_verification": True,
                "confidence": min(
                    *(
                        _component_by_id(extraction_result, match.component_id).confidence
                        for match in candidates
                    ),
                    _line_by_id(extraction_result, line_id).confidence,
                ),
                "evidence_ids": list(
                    _merge_evidence_ids(
                        _line_by_id(extraction_result, line_id).evidence_ids,
                        *(
                            _component_by_id(
                                extraction_result, match.component_id
                            ).evidence_ids
                            for match in candidates
                        ),
                    )
                ),
            }
        )

    return TopologyResult(
        document_id=extraction_result.document_id,
        nodes=tuple(nodes),
        edges=tuple(edges),
        uncertainties=tuple(uncertainties),
    )


def _build_nodes(extraction_result: ExtractionResult) -> list[TopologyNode]:
    nodes = [
        TopologyNode(
            id=component.id,
            type=component.type,
            confidence=component.confidence,
            attributes={"tag": component.tag} if component.tag is not None else {},
            evidence_ids=component.evidence_ids,
        )
        for component in extraction_result.entities
    ]
    nodes.extend(
        TopologyNode(
            id=line.line_id,
            type="line",
            confidence=line.confidence,
            evidence_ids=line.evidence_ids,
        )
        for line in extraction_result.line_candidates
    )
    return nodes


def _find_matches(
    extraction_result: ExtractionResult,
    config: EndpointMatchingConfig,
) -> list[EndpointMatch]:
    matches: list[EndpointMatch] = []
    for component in extraction_result.entities:
        for point_index, connection_point in enumerate(component.connection_points):
            for line in extraction_result.line_candidates:
                for endpoint_name, endpoint in (
                    ("start", line.start),
                    ("end", line.end),
                ):
                    if points_close(connection_point, endpoint, config.endpoint_tolerance):
                        matches.append(
                            EndpointMatch(
                                component_id=component.id,
                                line_id=line.line_id,
                                component_point_index=point_index,
                                line_endpoint=endpoint_name,
                                distance=distance(connection_point, endpoint),
                            )
                        )
    return matches


def _ambiguous_endpoint_keys(
    matches: list[EndpointMatch],
) -> set[tuple[str, str]]:
    candidates_by_endpoint: dict[tuple[str, str], set[str]] = {}
    for match in matches:
        candidates_by_endpoint.setdefault(
            (match.line_id, match.line_endpoint), set()
        ).add(match.component_id)
    return {
        key for key, component_ids in candidates_by_endpoint.items()
        if len(component_ids) > 1
    }


def _deduplicate_matches(matches: list[EndpointMatch]) -> list[EndpointMatch]:
    best_matches: dict[tuple[str, str, str], EndpointMatch] = {}
    for match in matches:
        key = (match.component_id, match.line_id, match.line_endpoint)
        current = best_matches.get(key)
        if current is None or (match.distance, match.component_point_index) < (
            current.distance,
            current.component_point_index,
        ):
            best_matches[key] = match
    return list(best_matches.values())


def _component_by_id(extraction_result: ExtractionResult, component_id: str):
    return next(component for component in extraction_result.entities if component.id == component_id)


def _line_by_id(extraction_result: ExtractionResult, line_id: str):
    return next(line for line in extraction_result.line_candidates if line.line_id == line_id)


def _merge_evidence_ids(*evidence_groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for group in evidence_groups:
        for evidence_id in group:
            if evidence_id not in merged:
                merged.append(evidence_id)
    return tuple(merged)
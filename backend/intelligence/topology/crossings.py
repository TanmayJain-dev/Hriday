"""Deterministic classification of line intersections."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Any

from backend.intelligence.extraction.models import ExtractionResult, LineCandidate, Point

from .geometry import IntersectionKind, intersect_segments, points_close
from .junctions import JunctionMatchingConfig, reconstruct_junctions
from .models import TopologyResult


class CrossingKind(str, Enum):
    CONFIRMED_JUNCTION = "confirmed_junction"
    NON_CONNECTED_CROSSING = "non_connected_crossing"
    AMBIGUOUS = "ambiguous"
    COLLINEAR_OVERLAP = "collinear_overlap"


@dataclass(frozen=True)
class CrossingClassification:
    line_ids: tuple[str, str]
    kind: CrossingKind
    point: Point | None = None
    confidence: float | None = None
    evidence_ids: tuple[str, ...] = ()
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "line_ids": list(self.line_ids),
            "kind": self.kind.value,
            "confidence": self.confidence,
            "evidence_ids": list(self.evidence_ids),
        }
        if self.point is not None:
            result["point"] = self.point.to_dict()
        if self.reason is not None:
            result["reason"] = self.reason
        return result


@dataclass(frozen=True)
class CrossingClassificationConfig:
    """Engineering tolerance for intersection classification."""

    intersection_tolerance: float

    def __post_init__(self) -> None:
        if self.intersection_tolerance < 0.0 or not math.isfinite(self.intersection_tolerance):
            raise ValueError("intersection_tolerance must be finite and non-negative")


def classify_crossings(
    extraction_result: ExtractionResult,
    config: CrossingClassificationConfig,
) -> tuple[CrossingClassification, ...]:
    """Classify every pairwise line intersection without creating edges.

    Endpoint involvement or a matching explicit junction candidate confirms a
    junction. A clean interior-to-interior point intersection without junction
    evidence is classified as non-connected. Conflicting extraction evidence
    is retained as ambiguous. Collinear overlap is never a junction.
    """
    lines = tuple(sorted(extraction_result.line_candidates, key=lambda line: line.line_id))
    classifications: list[CrossingClassification] = []
    for index, first in enumerate(lines):
        for second in lines[index + 1:]:
            intersection = intersect_segments(
                first.start,
                first.end,
                second.start,
                second.end,
                config.intersection_tolerance,
            )
            if intersection.kind is IntersectionKind.NONE:
                continue
            evidence_ids = _merge_ids(first.evidence_ids, second.evidence_ids)
            if intersection.kind is IntersectionKind.OVERLAP:
                classifications.append(
                    CrossingClassification(
                        line_ids=(first.line_id, second.line_id),
                        kind=CrossingKind.COLLINEAR_OVERLAP,
                        evidence_ids=evidence_ids,
                        reason="collinear_overlap_not_classified_as_junction",
                    )
                )
                continue

            point = intersection.point
            if point is None:
                continue
            candidate = _matching_candidate(extraction_result, point, config.intersection_tolerance)
            endpoint_supported = _endpoint_supported(
                first, second, point, config.intersection_tolerance
            )
            if candidate is not None and _candidate_conflicts(candidate):
                kind = CrossingKind.AMBIGUOUS
                reason = "conflicting_junction_candidate_evidence"
                confidence = candidate.confidence
                candidate_ids = candidate.evidence_ids
            elif endpoint_supported or candidate is not None:
                kind = CrossingKind.CONFIRMED_JUNCTION
                reason = "endpoint_contact" if endpoint_supported else "explicit_junction_candidate"
                confidence = min(
                    first.confidence,
                    second.confidence,
                    candidate.confidence if candidate is not None else 1.0,
                )
                candidate_ids = candidate.evidence_ids if candidate is not None else ()
            else:
                kind = CrossingKind.NON_CONNECTED_CROSSING
                reason = "interior_intersection_without_junction_evidence"
                confidence = min(first.confidence, second.confidence)
                candidate_ids = ()
            classifications.append(
                CrossingClassification(
                    line_ids=(first.line_id, second.line_id),
                    kind=kind,
                    point=point,
                    confidence=confidence,
                    evidence_ids=_merge_ids(evidence_ids, candidate_ids),
                    reason=reason,
                )
            )
    return tuple(classifications)


def reconstruct_with_crossing_classification(
    extraction_result: ExtractionResult,
    config: CrossingClassificationConfig,
    junction_tolerance: float | None = None,
) -> TopologyResult:
    """Return Phase 4 topology plus explicit Phase 5 crossing outcomes."""
    base = reconstruct_junctions(
        extraction_result,
        JunctionMatchingConfig(
            config.intersection_tolerance
            if junction_tolerance is None
            else junction_tolerance
        ),
    )
    classifications = classify_crossings(extraction_result, config)
    blocked_junction_ids = {
        _junction_id(classification.point)
        for classification in classifications
        if classification.point is not None
        and classification.kind
        in {CrossingKind.AMBIGUOUS, CrossingKind.COLLINEAR_OVERLAP}
    }
    line_by_id = {line.line_id: line for line in extraction_result.line_candidates}
    for classification in classifications:
        if classification.kind is not CrossingKind.COLLINEAR_OVERLAP:
            continue
        first = line_by_id[classification.line_ids[0]]
        second = line_by_id[classification.line_ids[1]]
        intersection = intersect_segments(
            first.start,
            first.end,
            second.start,
            second.end,
            config.intersection_tolerance,
        )
        for point in (intersection.overlap_start, intersection.overlap_end):
            if point is not None:
                blocked_junction_ids.add(_junction_id(point))
    nodes = tuple(node for node in base.nodes if node.id not in blocked_junction_ids)
    edges = tuple(
        edge
        for edge in base.edges
        if edge.target not in blocked_junction_ids and edge.source not in blocked_junction_ids
    )
    crossing_uncertainties = [
        classification.to_dict()
        for classification in classifications
        if classification.kind in {
            CrossingKind.AMBIGUOUS,
            CrossingKind.COLLINEAR_OVERLAP,
        }
    ]
    non_connected = [
        classification.to_dict()
        for classification in classifications
        if classification.kind is CrossingKind.NON_CONNECTED_CROSSING
    ]
    return TopologyResult(
        document_id=base.document_id,
        nodes=nodes,
        edges=edges,
        uncertainties=tuple(
            [uncertainty for uncertainty in base.uncertainties if not _is_phase5_crossing_uncertainty(uncertainty)]
            + crossing_uncertainties
            + non_connected
        ),
    )


def _endpoint_supported(
    first: LineCandidate,
    second: LineCandidate,
    point: Point,
    tolerance: float,
) -> bool:
    first_endpoint = _is_endpoint(first, point, tolerance)
    second_endpoint = _is_endpoint(second, point, tolerance)
    return first_endpoint or second_endpoint


def _is_endpoint(line: LineCandidate, point: Point, tolerance: float) -> bool:
    return points_close(point, line.start, tolerance) or points_close(point, line.end, tolerance)


def _matching_candidate(
    extraction_result: ExtractionResult,
    point: Point,
    tolerance: float,
):
    candidates = [
        candidate
        for candidate in extraction_result.junction_candidates
        if points_close(candidate.point, point, tolerance)
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda candidate: candidate.junction_id)[0]


def _candidate_conflicts(candidate: Any) -> bool:
    classification = str(candidate.attributes.get("classification", "")).lower()
    return classification in {"crossing", "non_connected_crossing", "ambiguous"}


def _is_phase5_crossing_uncertainty(uncertainty: dict[str, Any]) -> bool:
    return uncertainty.get("reason") == "interior_intersection_requires_junction_classification"


def _merge_ids(*groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for group in groups:
        for evidence_id in group:
            if evidence_id not in merged:
                merged.append(evidence_id)
    return tuple(merged)


def _junction_id(point: Point) -> str:
    return f"JUNCTION-{point.x:.12g}-{point.y:.12g}"
"""Deterministic reconstruction of supported line-line junctions."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from backend.intelligence.extraction.models import (
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)

from .connectivity import _merge_evidence_ids
from .geometry import (
    IntersectionKind,
    intersect_segments,
    point_on_segment,
    points_close,
)
from .models import TopologyEdge, TopologyNode, TopologyResult


@dataclass(frozen=True)
class JunctionMatchingConfig:
    """Engineering tolerance for deciding whether geometry shares a junction."""

    junction_tolerance: float

    def __post_init__(self) -> None:
        if self.junction_tolerance < 0.0 or not math.isfinite(self.junction_tolerance):
            raise ValueError("junction_tolerance must be finite and non-negative")


@dataclass(frozen=True)
class _JunctionAnchor:
    point: Point
    confidence: float
    evidence_ids: tuple[str, ...]
    explicit: bool


def reconstruct_junctions(
    extraction_result: ExtractionResult,
    config: JunctionMatchingConfig,
) -> TopologyResult:
    """Build line-to-junction relationships from supported geometric evidence.

    Endpoint-to-endpoint and endpoint-to-interior contacts are supported. An
    interior-to-interior crossing is unresolved unless an extracted
    ``JunctionCandidate`` validates it. Collinear overlap is never silently
    converted into a junction.
    """
    lines = tuple(sorted(extraction_result.line_candidates, key=lambda line: line.line_id))
    anchors = _build_anchors(extraction_result, lines, config.junction_tolerance)
    nodes = [
        _line_node(line)
        for line in lines
    ]
    edges: list[TopologyEdge] = []
    uncertainties: list[dict[str, Any]] = []
    emitted_junctions: set[str] = set()

    for anchor in anchors:
        participating = tuple(
            line for line in lines if _line_touches(line, anchor.point, config.junction_tolerance)
        )
        if len(participating) < 2:
            if anchor.explicit:
                uncertainties.append(_unsupported_candidate_uncertainty(anchor, participating))
            continue

        overlap_pairs = _overlap_pairs(participating, anchor.point, config.junction_tolerance)
        if overlap_pairs and not anchor.explicit:
            uncertainties.append(
                _overlap_uncertainty(anchor, participating, overlap_pairs)
            )
            continue

        junction_id = _junction_id(anchor.point)
        if junction_id in emitted_junctions:
            continue
        emitted_junctions.add(junction_id)
        line_confidence = min(line.confidence for line in participating)
        confidence = min(line_confidence, anchor.confidence)
        evidence_ids = _merge_evidence_ids(
            anchor.evidence_ids,
            *(line.evidence_ids for line in participating),
        )
        nodes.append(
            TopologyNode(
                id=junction_id,
                type="junction",
                confidence=confidence,
                evidence_ids=evidence_ids,
                attributes={
                    "point": anchor.point.to_dict(),
                    "line_ids": [line.line_id for line in participating],
                    "explicit_candidate": anchor.explicit,
                },
            )
        )
        for line in participating:
            edges.append(
                TopologyEdge(
                    source=line.line_id,
                    target=junction_id,
                    relationship="CONNECTED_TO",
                    confidence=confidence,
                    evidence_ids=evidence_ids,
                    attributes={"junction_point": anchor.point.to_dict()},
                )
            )

    uncertainties.extend(
        _interior_crossing_uncertainties(lines, anchors, config.junction_tolerance)
    )
    return TopologyResult(
        document_id=extraction_result.document_id,
        nodes=tuple(nodes),
        edges=tuple(edges),
        uncertainties=tuple(uncertainties),
    )


def _build_anchors(
    extraction_result: ExtractionResult,
    lines: tuple[LineCandidate, ...],
    tolerance: float,
) -> tuple[_JunctionAnchor, ...]:
    anchors: list[_JunctionAnchor] = []
    for line in lines:
        for point in (line.start, line.end):
            anchors.append(
                _JunctionAnchor(
                    point=point,
                    confidence=line.confidence,
                    evidence_ids=line.evidence_ids,
                    explicit=False,
                )
            )
    for candidate in sorted(
        extraction_result.junction_candidates,
        key=lambda item: (item.point.x, item.point.y, item.junction_id),
    ):
        anchors.append(
            _JunctionAnchor(
                point=candidate.point,
                confidence=candidate.confidence,
                evidence_ids=candidate.evidence_ids,
                explicit=True,
            )
        )
    return _merge_anchors(anchors, tolerance)


def _merge_anchors(
    anchors: list[_JunctionAnchor],
    tolerance: float,
) -> tuple[_JunctionAnchor, ...]:
    merged: list[_JunctionAnchor] = []
    for anchor in anchors:
        existing = next(
            (item for item in merged if points_close(item.point, anchor.point, tolerance)),
            None,
        )
        if existing is None:
            merged.append(anchor)
            continue
        merged.remove(existing)
        merged.append(
            _JunctionAnchor(
                point=existing.point,
                confidence=min(existing.confidence, anchor.confidence),
                evidence_ids=_merge_evidence_ids(existing.evidence_ids, anchor.evidence_ids),
                explicit=existing.explicit or anchor.explicit,
            )
        )
    return tuple(sorted(merged, key=lambda item: (item.point.x, item.point.y)))


def _line_node(line: LineCandidate) -> TopologyNode:
    return TopologyNode(
        id=line.line_id,
        type="line",
        confidence=line.confidence,
        evidence_ids=line.evidence_ids,
    )


def _line_touches(line: LineCandidate, point: Point, tolerance: float) -> bool:
    return point_on_segment(point, line.start, line.end, tolerance)


def _overlap_pairs(
    lines: tuple[LineCandidate, ...],
    point: Point,
    tolerance: float,
) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for index, first in enumerate(lines):
        for second in lines[index + 1:]:
            intersection = intersect_segments(
                first.start, first.end, second.start, second.end, tolerance
            )
            if intersection.kind is not IntersectionKind.OVERLAP:
                continue
            if (
                intersection.overlap_start is not None
                and intersection.overlap_end is not None
                and point_on_segment(
                    point,
                    intersection.overlap_start,
                    intersection.overlap_end,
                    tolerance,
                )
            ):
                pairs.append((first.line_id, second.line_id))
    return tuple(pairs)


def _overlap_uncertainty(
    anchor: _JunctionAnchor,
    lines: tuple[LineCandidate, ...],
    overlap_pairs: tuple[tuple[str, str], ...],
) -> dict[str, Any]:
    return {
        "point": anchor.point.to_dict(),
        "line_ids": [line.line_id for line in lines],
        "overlap_pairs": [list(pair) for pair in overlap_pairs],
        "reason": "collinear_overlap_not_classified_as_junction",
        "requires_verification": True,
        "evidence_ids": list(
            _merge_evidence_ids(anchor.evidence_ids, *(line.evidence_ids for line in lines))
        ),
    }


def _unsupported_candidate_uncertainty(
    anchor: _JunctionAnchor,
    lines: tuple[LineCandidate, ...],
) -> dict[str, Any]:
    return {
        "point": anchor.point.to_dict(),
        "line_ids": [line.line_id for line in lines],
        "reason": "junction_candidate_lacks_two_supporting_lines",
        "requires_verification": True,
        "evidence_ids": list(anchor.evidence_ids),
    }


def _interior_crossing_uncertainties(
    lines: tuple[LineCandidate, ...],
    anchors: tuple[_JunctionAnchor, ...],
    tolerance: float,
) -> list[dict[str, Any]]:
    uncertainties: list[dict[str, Any]] = []
    for index, first in enumerate(lines):
        for second in lines[index + 1:]:
            intersection = intersect_segments(
                first.start, first.end, second.start, second.end, tolerance
            )
            if intersection.kind is not IntersectionKind.POINT or intersection.point is None:
                continue
            point = intersection.point
            first_endpoint = points_close(point, first.start, tolerance) or points_close(
                point, first.end, tolerance
            )
            second_endpoint = points_close(point, second.start, tolerance) or points_close(
                point, second.end, tolerance
            )
            explicit = any(
                anchor.explicit and points_close(anchor.point, point, tolerance)
                for anchor in anchors
            )
            if first_endpoint or second_endpoint or explicit:
                continue
            uncertainties.append(
                {
                    "point": point.to_dict(),
                    "line_ids": [first.line_id, second.line_id],
                    "reason": "interior_intersection_requires_junction_classification",
                    "requires_verification": True,
                    "evidence_ids": list(
                        _merge_evidence_ids(first.evidence_ids, second.evidence_ids)
                    ),
                }
            )
    return uncertainties


def _junction_id(point: Point) -> str:
    return f"JUNCTION-{point.x:.12g}-{point.y:.12g}"
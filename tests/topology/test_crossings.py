from backend.intelligence.topology.models import (
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.crossings import (
    CrossingClassificationConfig,
    CrossingKind,
    classify_crossings,
    reconstruct_with_crossing_classification,
)


def line(line_id, start, end, confidence=0.9, evidence_ids=()):
    return LineCandidate(line_id, start, end, confidence, evidence_ids=evidence_ids)


def result(lines, candidates=()):
    return ExtractionResult(
        document_id="synthetic-crossing-001",
        line_candidates=tuple(lines),
        junction_candidates=tuple(candidates),
    )


def classify(extraction, tolerance=0.001):
    return classify_crossings(extraction, CrossingClassificationConfig(tolerance))


def test_explicit_candidate_confirms_interior_junction_with_provenance():
    classifications = classify(
        result(
            [
                line("L-001", Point(0, 0), Point(10, 10), evidence_ids=("ev-a",)),
                line("L-002", Point(0, 10), Point(10, 0), evidence_ids=("ev-b",)),
            ],
            [JunctionCandidate("J-1", Point(5, 5), 0.8, evidence_ids=("ev-j",))],
        )
    )

    assert classifications[0].kind is CrossingKind.CONFIRMED_JUNCTION
    assert classifications[0].confidence == 0.8
    assert classifications[0].evidence_ids == ("ev-a", "ev-b", "ev-j")


def test_ordinary_x_crossing_is_non_connected_without_edges():
    extraction = result([
        line("L-001", Point(0, 0), Point(10, 10)),
        line("L-002", Point(0, 10), Point(10, 0)),
    ])

    classifications = classify(extraction)
    topology = reconstruct_with_crossing_classification(
        extraction, CrossingClassificationConfig(0.001)
    )
    assert classifications[0].kind is CrossingKind.NON_CONNECTED_CROSSING
    assert topology.edges == ()
    assert topology.uncertainties[0]["kind"] == "non_connected_crossing"


def test_endpoint_interior_intersection_is_confirmed_by_phase4_rule():
    classifications = classify(
        result([
            line("L-001", Point(5, 0), Point(5, 5)),
            line("L-002", Point(0, 0), Point(10, 0)),
        ])
    )

    assert classifications[0].kind is CrossingKind.CONFIRMED_JUNCTION


def test_conflicting_candidate_is_ambiguous_and_requires_review():
    extraction = result(
        [
            line("L-001", Point(0, 0), Point(10, 10)),
            line("L-002", Point(0, 10), Point(10, 0)),
        ],
        [
            JunctionCandidate(
                "J-1",
                Point(5, 5),
                0.7,
                attributes={"classification": "crossing"},
            )
        ],
    )
    classifications = classify(extraction)
    topology = reconstruct_with_crossing_classification(
        extraction, CrossingClassificationConfig(0.001)
    )

    assert classifications[0].kind is CrossingKind.AMBIGUOUS
    assert classifications[0].reason == "conflicting_junction_candidate_evidence"
    assert topology.edges == ()
    assert all(node.type != "junction" for node in topology.nodes)


def test_multiple_intersections_are_classified_deterministically_without_direction():
    extraction = result([
        line("L-003", Point(5, -5), Point(5, 15), evidence_ids=("ev-3",)),
        line("L-001", Point(0, 0), Point(10, 0), evidence_ids=("ev-1",)),
        line("L-002", Point(0, 10), Point(10, 10), evidence_ids=("ev-2",)),
    ])

    first = tuple(item.to_dict() for item in classify(extraction))
    second = tuple(item.to_dict() for item in classify(extraction))
    assert first == second
    assert len(first) == 2
    assert all(item["kind"] == "non_connected_crossing" for item in first)


def test_near_miss_and_collinear_overlap_are_not_confirmed_junctions():
    near_miss = classify(
        result([
            line("L-001", Point(0, 0), Point(5, 0)),
            line("L-002", Point(5.01, 0), Point(10, 0)),
        ])
    )
    overlap = classify(
        result([
            line("L-001", Point(0, 0), Point(10, 0)),
            line("L-002", Point(5, 0), Point(15, 0)),
        ])
    )

    assert near_miss == ()
    assert overlap[0].kind is CrossingKind.COLLINEAR_OVERLAP


def test_tolerance_boundary_and_no_duplicate_edges():
    extraction = result([
        line("L-001", Point(0, 0), Point(5, 0)),
        line("L-002", Point(5.125, 0), Point(10, 0)),
    ])
    topology = reconstruct_with_crossing_classification(
        extraction, CrossingClassificationConfig(0.125)
    )

    assert len(topology.edges) == 2
    assert len({(edge.source, edge.target) for edge in topology.edges}) == 2
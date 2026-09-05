from backend.intelligence.extraction.models import (
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.junctions import (
    JunctionMatchingConfig,
    reconstruct_junctions,
)


def make_line(
    line_id: str,
    start: Point,
    end: Point,
    confidence: float = 0.9,
    evidence_ids: tuple[str, ...] = (),
) -> LineCandidate:
    return LineCandidate(line_id, start, end, confidence, evidence_ids=evidence_ids)


def make_result(
    lines: tuple[LineCandidate, ...],
    candidates: tuple[JunctionCandidate, ...] = (),
) -> ExtractionResult:
    return ExtractionResult(
        document_id="synthetic-junction-001",
        line_candidates=lines,
        junction_candidates=candidates,
    )


def reconstruct(result: ExtractionResult, tolerance: float = 0.001):
    return reconstruct_junctions(result, JunctionMatchingConfig(tolerance))


def junction_nodes(result):
    return [node for node in result.nodes if node.type == "junction"]


def test_two_line_endpoints_meeting_create_one_deterministic_junction():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(5, 0)),
                make_line("L-002", Point(5, 0), Point(10, 0)),
            )
        )
    )

    nodes = junction_nodes(result)
    assert [node.id for node in nodes] == ["JUNCTION-5-0"]
    assert {(edge.source, edge.target) for edge in result.edges} == {
        ("L-001", "JUNCTION-5-0"),
        ("L-002", "JUNCTION-5-0"),
    }


def test_three_line_endpoints_converging_create_one_junction():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(5, 5)),
                make_line("L-002", Point(5, 5), Point(10, 5)),
                make_line("L-003", Point(5, 5), Point(5, 10)),
            )
        )
    )

    assert len(junction_nodes(result)) == 1
    assert len(result.edges) == 3


def test_t_junction_connects_endpoint_to_other_line_interior():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(5, 0), Point(5, 5)),
                make_line("L-002", Point(0, 0), Point(10, 0)),
            )
        )
    )

    assert len(junction_nodes(result)) == 1
    assert {edge.source for edge in result.edges} == {"L-001", "L-002"}


def test_explicit_junction_candidate_supports_interior_intersection():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(10, 10), evidence_ids=("ev-a",)),
                make_line("L-002", Point(0, 10), Point(10, 0), evidence_ids=("ev-b",)),
            ),
            (
                JunctionCandidate(
                    "J-CAND-1", Point(5, 5), 0.8, evidence_ids=("ev-junction",)
                ),
            ),
        )
    )

    node = junction_nodes(result)[0]
    assert node.id == "JUNCTION-5-5"
    assert node.evidence_ids == ("ev-junction", "ev-a", "ev-b")
    assert len(result.edges) == 2


def test_near_miss_outside_tolerance_stays_disconnected():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(5, 0)),
                make_line("L-002", Point(5.01, 0), Point(10, 0)),
            )
        ),
        tolerance=0.001,
    )

    assert junction_nodes(result) == []
    assert result.edges == ()


def test_endpoint_at_tolerance_boundary_is_connected():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(5, 0)),
                make_line("L-002", Point(5.125, 0), Point(10, 0)),
            )
        ),
        tolerance=0.125,
    )

    assert len(junction_nodes(result)) == 1
    assert len(result.edges) == 2


def test_interior_crossing_without_candidate_is_uncertain_not_connected():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(10, 10)),
                make_line("L-002", Point(0, 10), Point(10, 0)),
            )
        )
    )

    assert junction_nodes(result) == []
    assert result.edges == ()
    assert result.uncertainties[0]["reason"] == (
        "interior_intersection_requires_junction_classification"
    )


def test_collinear_overlap_is_uncertain_not_a_junction():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(10, 0)),
                make_line("L-002", Point(5, 0), Point(15, 0)),
            )
        )
    )

    assert junction_nodes(result) == []
    assert result.edges == ()
    assert any(
        uncertainty["reason"] == "collinear_overlap_not_classified_as_junction"
        for uncertainty in result.uncertainties
    )


def test_confidence_and_provenance_are_conservative_and_preserved():
    result = reconstruct(
        make_result(
            (
                make_line("L-001", Point(0, 0), Point(5, 0), 0.95, ("ev-1",)),
                make_line("L-002", Point(5, 0), Point(10, 0), 0.72, ("ev-2",)),
            )
        )
    )

    node = junction_nodes(result)[0]
    assert node.confidence == 0.72
    assert node.evidence_ids == ("ev-1", "ev-2")
    assert all(edge.confidence == 0.72 for edge in result.edges)
    assert all(edge.evidence_ids == ("ev-1", "ev-2") for edge in result.edges)


def test_junction_output_is_deterministic_and_has_no_flow_direction():
    extraction = make_result(
        (
            make_line("L-002", Point(10, 0), Point(5, 0)),
            make_line("L-001", Point(0, 0), Point(5, 0)),
        )
    )

    first = reconstruct(extraction).to_dict()
    second = reconstruct(extraction).to_dict()
    assert first == second
    assert {edge.source for edge in reconstruct(extraction).edges} == {"L-001", "L-002"}
    assert all(edge.target == "JUNCTION-5-0" for edge in reconstruct(extraction).edges)


def test_ambiguous_explicit_candidate_without_two_supporting_lines_requires_review():
    result = reconstruct(
        make_result(
            (make_line("L-001", Point(0, 0), Point(10, 0)),),
            (JunctionCandidate("J-CAND-1", Point(5, 0), 0.9),),
        )
    )

    assert junction_nodes(result) == []
    assert result.uncertainties[0]["requires_verification"] is True
from backend.intelligence.extraction.models import (
    ComponentObservation,
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.reconstruction import (
    DeterministicTopologyReconstructor,
    TopologyReconstructionConfig,
    reconstruct_topology,
)


CONFIG = TopologyReconstructionConfig(
    endpoint_tolerance=0.001,
    junction_tolerance=0.001,
    intersection_tolerance=0.001,
)


def line(line_id, start, end, confidence=0.9, evidence_ids=()):
    return LineCandidate(line_id, start, end, confidence, evidence_ids=evidence_ids)


def component(component_id, point, confidence=0.95, evidence_ids=()):
    return ComponentObservation(
        component_id,
        "equipment",
        confidence,
        connection_points=(point,),
        evidence_ids=evidence_ids,
    )


def test_full_pipeline_merges_component_line_and_junction_connectivity():
    extraction = ExtractionResult(
        document_id="synthetic-full-001",
        entities=(component("P-101", Point(0, 0), evidence_ids=("ev-pump",)),),
        line_candidates=(
            line("L-001", Point(0, 0), Point(5, 0), evidence_ids=("ev-l1",)),
            line("L-002", Point(5, 0), Point(10, 0), evidence_ids=("ev-l2",)),
        ),
    )

    result = reconstruct_topology(extraction, CONFIG)
    assert {(edge.source, edge.target) for edge in result.edges} == {
        ("P-101", "L-001"),
        ("L-001", "JUNCTION-5-0"),
        ("L-002", "JUNCTION-5-0"),
    }
    assert {node.id for node in result.nodes} == {
        "P-101",
        "L-001",
        "L-002",
        "JUNCTION-5-0",
    }


def test_t_junction_and_multiple_lines_preserve_component_and_junction_facts():
    extraction = ExtractionResult(
        document_id="synthetic-full-002",
        entities=(component("P-101", Point(5, 0), evidence_ids=("ev-pump",)),),
        line_candidates=(
            line("L-001", Point(5, 0), Point(5, 5), evidence_ids=("ev-l1",)),
            line("L-002", Point(0, 0), Point(10, 0), evidence_ids=("ev-l2",)),
            line("L-003", Point(5, 0), Point(5, -5), evidence_ids=("ev-l3",)),
        ),
    )

    result = reconstruct_topology(extraction, CONFIG)
    assert ("P-101", "L-001") in {
        (edge.source, edge.target) for edge in result.edges
    }
    assert len([edge for edge in result.edges if edge.target == "JUNCTION-5-0"]) == 3


def test_x_crossing_is_not_leaked_as_connected_and_is_preserved_as_classification():
    extraction = ExtractionResult(
        document_id="synthetic-full-crossing",
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 10)),
            line("L-002", Point(0, 10), Point(10, 0)),
        ),
    )

    result = reconstruct_topology(extraction, CONFIG)
    assert result.edges == ()
    assert any(item["kind"] == "non_connected_crossing" for item in result.uncertainties)


def test_explicit_junction_candidate_connects_intersection_with_merged_provenance():
    extraction = ExtractionResult(
        document_id="synthetic-full-explicit",
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 10), 0.95, ("ev-a",)),
            line("L-002", Point(0, 10), Point(10, 0), 0.85, ("ev-b",)),
        ),
        junction_candidates=(
            JunctionCandidate("J-1", Point(5, 5), 0.8, ("ev-j",)),
        ),
    )

    result = reconstruct_topology(extraction, CONFIG)
    assert len(result.edges) == 2
    junction = next(node for node in result.nodes if node.type == "junction")
    assert junction.id == "JUNCTION-5-5"
    assert junction.evidence_ids == ("ev-j", "ev-a", "ev-b")
    assert all(edge.confidence == 0.8 for edge in result.edges)


def test_ambiguous_and_overlap_cases_remain_unresolved():
    ambiguous = ExtractionResult(
        document_id="synthetic-full-ambiguous",
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 10)),
            line("L-002", Point(0, 10), Point(10, 0)),
        ),
        junction_candidates=(
            JunctionCandidate(
                "J-1",
                Point(5, 5),
                0.7,
                attributes={"classification": "crossing"},
            ),
        ),
    )
    overlap = ExtractionResult(
        document_id="synthetic-full-overlap",
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 0)),
            line("L-002", Point(5, 0), Point(15, 0)),
        ),
    )

    ambiguous_result = reconstruct_topology(ambiguous, CONFIG)
    overlap_result = reconstruct_topology(overlap, CONFIG)
    assert ambiguous_result.edges == ()
    assert overlap_result.edges == ()
    assert any(item["kind"] == "ambiguous" for item in ambiguous_result.uncertainties)
    assert any(item["kind"] == "collinear_overlap" for item in overlap_result.uncertainties)


def test_empty_input_and_repeated_input_are_stable():
    extraction = ExtractionResult(document_id="synthetic-empty")
    first = reconstruct_topology(extraction, CONFIG)
    second = reconstruct_topology(extraction, CONFIG)
    assert first.to_dict() == second.to_dict()
    assert first.nodes == ()
    assert first.edges == ()
    assert first.uncertainties == ()


def test_uncertainties_are_aggregated_without_duplicates_and_provider_matches_protocol():
    extraction = ExtractionResult(
        document_id="synthetic-full-uncertainty",
        uncertainties=({"reason": "source_uncertainty", "requires_verification": True},),
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 10)),
            line("L-002", Point(0, 10), Point(10, 0)),
        ),
    )

    function_result = reconstruct_topology(extraction, CONFIG)
    provider_result = DeterministicTopologyReconstructor(CONFIG).reconstruct(extraction)
    assert function_result.to_dict() == provider_result.to_dict()
    assert len(
        [item for item in function_result.uncertainties if item["reason"] == "source_uncertainty"]
    ) == 1


def test_provenance_less_generated_edge_becomes_review_uncertainty():
    extraction = ExtractionResult(
        document_id="synthetic-missing-provenance",
        entities=(component("P-101", Point(0, 0)),),
        line_candidates=(line("L-001", Point(0, 0), Point(5, 0)),),
    )

    result = reconstruct_topology(extraction, CONFIG)
    assert result.edges == ()
    uncertainty = next(
        item for item in result.uncertainties if item["reason"] == "missing_provenance"
    )
    assert uncertainty["confidence"] == 0.9
    assert uncertainty["requires_verification"] is True
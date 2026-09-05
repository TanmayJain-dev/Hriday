from backend.intelligence.topology.models import (
    ComponentObservation,
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.reconstruction import (
    TopologyReconstructionConfig,
    reconstruct_topology,
)


CONFIG = TopologyReconstructionConfig(0.001, 0.001, 0.001)


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


def test_component_endpoint_and_two_line_junction():
    extraction = ExtractionResult(
        "e2e-component-junction",
        entities=(component("P-101", Point(0, 0), evidence_ids=("ev-p",)),),
        line_candidates=(
            line("L-001", Point(0, 0), Point(5, 0), evidence_ids=("ev-l1",)),
            line("L-002", Point(5, 0), Point(10, 0), evidence_ids=("ev-l2",)),
        ),
    )

    topology = reconstruct_topology(extraction, CONFIG)

    assert topology.uncertainties == ()
    assert {edge.source for edge in topology.edges} == {"P-101", "L-001", "L-002"}
    assert {edge.target for edge in topology.edges} == {"L-001", "JUNCTION-5-0"}
    assert any(node.id == "JUNCTION-5-0" for node in topology.nodes)
    assert all(edge.confidence <= 0.9 for edge in topology.edges)
    assert all(edge.evidence_ids for edge in topology.edges)
    assert topology.document_id == "e2e-component-junction"


def test_t_junction_and_multiple_convergence_preserve_topology_facts():
    extraction = ExtractionResult(
        "e2e-t-junction",
        entities=(component("P-101", Point(5, 0), evidence_ids=("ev-p",)),),
        line_candidates=(
            line("L-001", Point(5, 0), Point(5, 5), evidence_ids=("ev-1",)),
            line("L-002", Point(0, 0), Point(10, 0), evidence_ids=("ev-2",)),
            line("L-003", Point(5, 0), Point(5, -5), evidence_ids=("ev-3",)),
        ),
    )

    topology = reconstruct_topology(extraction, CONFIG)

    assert topology.uncertainties == ()
    assert len(
        [edge for edge in topology.edges if edge.target == "JUNCTION-5-0"]
    ) == 3
    assert any(
        edge.source == "P-101" and edge.target == "L-001"
        for edge in topology.edges
    )


def test_explicit_intersection_is_confirmed_and_provenance_survives():
    extraction = ExtractionResult(
        "e2e-explicit",
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 10), 0.95, ("ev-a",)),
            line("L-002", Point(0, 10), Point(10, 0), 0.8, ("ev-b",)),
        ),
        junction_candidates=(
            JunctionCandidate("J-1", Point(5, 5), 0.7, ("ev-j",)),
        ),
    )

    topology = reconstruct_topology(extraction, CONFIG)

    assert topology.uncertainties == ()
    junction = next(
        node for node in topology.nodes if node.id == "JUNCTION-5-5"
    )
    assert junction.confidence == 0.7
    assert junction.evidence_ids == ("ev-j", "ev-a", "ev-b")


def test_crossing_and_overlap_never_become_topology_edges():
    cases = (
        ExtractionResult(
            "e2e-crossing",
            line_candidates=(
                line("L-001", Point(0, 0), Point(10, 10), evidence_ids=("ev-a",)),
                line("L-002", Point(0, 10), Point(10, 0), evidence_ids=("ev-b",)),
            ),
        ),
        ExtractionResult(
            "e2e-overlap",
            line_candidates=(
                line("L-001", Point(0, 0), Point(10, 0), evidence_ids=("ev-a",)),
                line("L-002", Point(5, 0), Point(15, 0), evidence_ids=("ev-b",)),
            ),
        ),
    )

    for extraction in cases:
        topology = reconstruct_topology(extraction, CONFIG)
        assert topology.edges == ()
        assert topology.uncertainties
        assert all(item.get("reason") or item.get("kind") for item in topology.uncertainties)


def test_conflicting_intersection_requires_verification():
    extraction = ExtractionResult(
        "e2e-ambiguous",
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 10), evidence_ids=("ev-a",)),
            line("L-002", Point(0, 10), Point(10, 0), evidence_ids=("ev-b",)),
        ),
        junction_candidates=(
            JunctionCandidate(
                "J-1",
                Point(5, 5),
                0.6,
                evidence_ids=("ev-j",),
                attributes={"classification": "crossing"},
            ),
        ),
    )

    topology = reconstruct_topology(extraction, CONFIG)

    assert topology.edges == ()
    assert any(
        item.get("kind") == "ambiguous"
        for item in topology.uncertainties
    )
    assert all(
        item.get("requires_verification") is True
        for item in topology.uncertainties
    )


def test_near_miss_and_missing_evidence_are_blocked_conservatively():
    near_miss = ExtractionResult(
        "e2e-near-miss",
        line_candidates=(
            line("L-001", Point(0, 0), Point(5, 0), evidence_ids=("ev-a",)),
            line("L-002", Point(5.01, 0), Point(10, 0), evidence_ids=("ev-b",)),
        ),
    )

    missing_evidence = ExtractionResult(
        "e2e-no-evidence",
        entities=(component("P-101", Point(0, 0)),),
        line_candidates=(
            line("L-001", Point(0, 0), Point(5, 0)),
        ),
    )

    near_topology = reconstruct_topology(near_miss, CONFIG)
    missing_topology = reconstruct_topology(missing_evidence, CONFIG)

    assert near_topology.edges == ()
    assert near_topology.uncertainties == ()

    assert missing_topology.edges == ()
    assert any(
        item["reason"] == "missing_provenance"
        for item in missing_topology.uncertainties
    )


def test_multiple_components_and_repeated_pipeline_output_are_deterministic():
    extraction = ExtractionResult(
        "e2e-repeatable",
        entities=(
            component("P-101", Point(0, 0), evidence_ids=("ev-p",)),
            component("V-102", Point(10, 0), evidence_ids=("ev-v",)),
        ),
        line_candidates=(
            line("L-001", Point(0, 0), Point(10, 0), evidence_ids=("ev-l",)),
        ),
    )

    first = reconstruct_topology(extraction, CONFIG)
    second = reconstruct_topology(extraction, CONFIG)

    assert first.to_dict() == second.to_dict()
    assert len(first.nodes) == len({node.id for node in first.nodes})
    assert len(first.edges) == len(
        {(edge.source, edge.target, edge.relationship) for edge in first.edges}
    )


def test_empty_extraction_produces_empty_topology():
    topology = reconstruct_topology(
        ExtractionResult("e2e-empty"),
        CONFIG,
    )

    assert topology.nodes == ()
    assert topology.edges == ()
    assert topology.uncertainties == ()
from backend.intelligence.extraction.models import (
    ComponentObservation,
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)
from backend.intelligence.graph.builder import build_graph_with_uncertainties
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


def graph_for(extraction):
    topology = reconstruct_topology(extraction, CONFIG)
    store, uncertainties = build_graph_with_uncertainties(topology.to_dict())
    return topology, store, uncertainties


def test_component_endpoint_and_two_line_junction_reach_graph():
    extraction = ExtractionResult(
        "e2e-component-junction",
        entities=(component("P-101", Point(0, 0), evidence_ids=("ev-p",)),),
        line_candidates=(
            line("L-001", Point(0, 0), Point(5, 0), evidence_ids=("ev-l1",)),
            line("L-002", Point(5, 0), Point(10, 0), evidence_ids=("ev-l2",)),
        ),
    )

    topology, store, uncertainties = graph_for(extraction)
    assert uncertainties == []
    assert {edge.source for edge in store.all_edges()} == {"P-101", "L-001", "L-002"}
    assert store.get_node("JUNCTION-5-0") is not None
    assert all(edge.confidence <= 0.9 for edge in store.all_edges())
    assert all(edge.evidence_ids for edge in store.all_edges())
    assert topology.to_dict()["document_id"] == "e2e-component-junction"


def test_t_junction_and_multiple_convergence_preserve_all_graph_facts():
    extraction = ExtractionResult(
        "e2e-t-junction",
        entities=(component("P-101", Point(5, 0), evidence_ids=("ev-p",)),),
        line_candidates=(
            line("L-001", Point(5, 0), Point(5, 5), evidence_ids=("ev-1",)),
            line("L-002", Point(0, 0), Point(10, 0), evidence_ids=("ev-2",)),
            line("L-003", Point(5, 0), Point(5, -5), evidence_ids=("ev-3",)),
        ),
    )

    _, store, uncertainties = graph_for(extraction)
    assert uncertainties == []
    assert len(store.get_edges(target="JUNCTION-5-0")) == 3
    assert store.get_edge("P-101", "L-001") is not None


def test_explicit_intersection_is_confirmed_and_provenance_survives_graph():
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

    _, store, uncertainties = graph_for(extraction)
    assert uncertainties == []
    junction = store.get_node("JUNCTION-5-5")
    assert junction is not None
    assert junction.confidence == 0.7
    assert junction.evidence_ids == ("ev-j", "ev-a", "ev-b")


def test_crossing_ambiguity_and_overlap_never_become_graph_edges():
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
        _, store, uncertainties = graph_for(extraction)
        assert store.all_edges() == []
        assert uncertainties
        assert all(item["reason"] or item["kind"] for item in uncertainties)


def test_conflicting_intersection_requires_verification_after_graph_boundary():
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

    _, store, uncertainties = graph_for(extraction)
    assert store.all_edges() == []
    assert any(item.get("kind") == "ambiguous" for item in uncertainties)
    assert all(item.get("requires_verification") is True for item in uncertainties)


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
        line_candidates=(line("L-001", Point(0, 0), Point(5, 0)),),
    )

    _, near_store, near_uncertainties = graph_for(near_miss)
    _, missing_store, missing_uncertainties = graph_for(missing_evidence)
    assert near_store.all_edges() == []
    assert near_uncertainties == []
    assert missing_store.all_edges() == []
    assert any(item["reason"] == "missing_provenance" for item in missing_uncertainties)


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

    first_topology, first_store, first_uncertainties = graph_for(extraction)
    second_topology, second_store, second_uncertainties = graph_for(extraction)
    assert first_topology.to_dict() == second_topology.to_dict()
    assert first_store.to_dict("e2e-repeatable") == second_store.to_dict("e2e-repeatable")
    assert first_uncertainties == second_uncertainties
    assert len(first_store.all_nodes()) == len({node.id for node in first_store.all_nodes()})
    assert len(first_store.all_edges()) == len({(edge.source, edge.target, edge.relationship) for edge in first_store.all_edges()})


def test_empty_extraction_produces_empty_graph():
    topology, store, uncertainties = graph_for(ExtractionResult("e2e-empty"))

    assert topology.nodes == ()
    assert topology.edges == ()
    assert store.all_nodes() == []
    assert store.all_edges() == []
    assert uncertainties == []
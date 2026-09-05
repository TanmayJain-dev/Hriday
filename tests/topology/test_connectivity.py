from backend.intelligence.extraction.models import (
    ComponentObservation,
    ExtractionResult,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.connectivity import (
    EndpointMatchingConfig,
    reconstruct_endpoint_connectivity,
)


def component(
    component_id: str,
    point: Point,
    confidence: float = 0.9,
    evidence_ids: tuple[str, ...] = (),
) -> ComponentObservation:
    return ComponentObservation(
        id=component_id,
        type="equipment",
        confidence=confidence,
        connection_points=(point,),
        evidence_ids=evidence_ids,
    )


def line(
    line_id: str = "L-001",
    start: Point = Point(0, 0),
    end: Point = Point(10, 0),
    confidence: float = 0.8,
    evidence_ids: tuple[str, ...] = (),
) -> LineCandidate:
    return LineCandidate(
        line_id=line_id,
        start=start,
        end=end,
        confidence=confidence,
        evidence_ids=evidence_ids,
    )


def result(*entities: ComponentObservation, lines: tuple[LineCandidate, ...] = ()):
    return ExtractionResult(
        document_id="synthetic-connectivity-001",
        entities=entities,
        line_candidates=lines,
    )


def test_exact_endpoint_match_creates_component_to_line_edge():
    topology = reconstruct_endpoint_connectivity(
        result(component("P-101", Point(0, 0)), lines=(line(),)),
        EndpointMatchingConfig(endpoint_tolerance=0.01),
    )

    assert len(topology.edges) == 1
    edge = topology.edges[0]
    assert (edge.source, edge.target) == ("P-101", "L-001")
    assert edge.attributes["line_endpoint"] == "start"


def test_endpoint_match_uses_configured_tolerance_and_rejects_outside_point():
    within = reconstruct_endpoint_connectivity(
        result(component("P-101", Point(0.0005, 0.0003)), lines=(line(),)),
        EndpointMatchingConfig(endpoint_tolerance=0.001),
    )
    outside = reconstruct_endpoint_connectivity(
        result(component("P-102", Point(0.002, 0)), lines=(line(),)),
        EndpointMatchingConfig(endpoint_tolerance=0.001),
    )

    assert len(within.edges) == 1
    assert outside.edges == ()


def test_both_line_endpoints_can_match_without_flow_direction():
    topology = reconstruct_endpoint_connectivity(
        result(
            component("P-101", Point(0, 0)),
            component("V-102", Point(10, 0)),
            lines=(line(evidence_ids=("ev-line",)),),
        ),
        EndpointMatchingConfig(endpoint_tolerance=0.001),
    )

    assert {(edge.source, edge.target) for edge in topology.edges} == {
        ("P-101", "L-001"),
        ("V-102", "L-001"),
    }
    assert {edge.attributes["line_endpoint"] for edge in topology.edges} == {"start", "end"}


def test_multiple_components_matching_one_endpoint_are_review_required():
    topology = reconstruct_endpoint_connectivity(
        result(
            component("P-101", Point(0, 0)),
            component("P-102", Point(0.0005, 0)),
            lines=(line(),),
        ),
        EndpointMatchingConfig(endpoint_tolerance=0.001),
    )

    assert topology.edges == ()
    assert len(topology.uncertainties) == 1
    uncertainty = topology.uncertainties[0]
    assert uncertainty["line_endpoint"] == "start"
    assert uncertainty["candidate_component_ids"] == ["P-101", "P-102"]
    assert uncertainty["requires_verification"] is True


def test_provenance_and_conservative_confidence_are_preserved():
    topology = reconstruct_endpoint_connectivity(
        result(
            component("P-101", Point(0, 0), confidence=0.93, evidence_ids=("ev-component",)),
            lines=(line(confidence=0.81, evidence_ids=("ev-line", "ev-shared")),),
        ),
        EndpointMatchingConfig(endpoint_tolerance=0.001),
    )

    edge = topology.edges[0]
    assert edge.confidence == 0.81
    assert edge.evidence_ids == ("ev-component", "ev-line", "ev-shared")


def test_endpoint_matching_does_not_create_component_to_component_shortcut():
    topology = reconstruct_endpoint_connectivity(
        result(
            component("P-101", Point(0, 0)),
            component("V-102", Point(10, 0)),
            lines=(line(),),
        ),
        EndpointMatchingConfig(endpoint_tolerance=0.001),
    )

    assert all(edge.target == "L-001" for edge in topology.edges)
    assert not any(
        edge.source == "P-101" and edge.target == "V-102"
        for edge in topology.edges
    )


def test_floating_point_endpoint_match_is_deterministic():
    topology = reconstruct_endpoint_connectivity(
        result(component("P-101", Point(10.0000004, -0.0000003)), lines=(line(),)),
        EndpointMatchingConfig(endpoint_tolerance=0.000001),
    )

    assert len(topology.edges) == 1
    assert topology.edges[0].attributes["line_endpoint"] == "end"


def test_endpoint_tolerance_must_be_finite_and_non_negative():
    for invalid_tolerance in (-0.1, float("inf")):
        try:
            EndpointMatchingConfig(endpoint_tolerance=invalid_tolerance)
            assert False, "Expected invalid endpoint tolerance to be rejected"
        except ValueError:
            pass
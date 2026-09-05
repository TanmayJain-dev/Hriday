from backend.intelligence.topology.models import (
    BoundingBox,
    ComponentObservation,
    ExtractionResult,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.models import (
    TopologyEdge,
    TopologyNode,
    TopologyResult,
)


def test_extraction_observations_round_trip_with_component_and_line_geometry():
    extraction = ExtractionResult(
        document_id="synthetic-001",
        entities=(
            ComponentObservation(
                id="P-101",
                type="pump",
                tag="P-101",
                confidence=0.97,
                bbox=BoundingBox(10, 20, 30, 40),
                connection_points=(Point(30, 30),),
                evidence_ids=("ev-pump-101",),
            ),
        ),
        line_candidates=(
            LineCandidate(
                line_id="L-001",
                start=Point(30, 30),
                end=Point(80, 30),
                confidence=0.91,
                evidence_ids=("ev-line-001",),
            ),
        ),
    )

    restored = ExtractionResult.from_dict(extraction.to_dict())
    assert restored == extraction
    assert restored.entities[0].tag == "P-101"
    assert restored.line_candidates[0].start == Point(30, 30)


def test_topology_result_represents_provenance_bearing_connection():
    result = TopologyResult(
        document_id="synthetic-001",
        nodes=(
            TopologyNode("P-101", "pump", confidence=0.97, evidence_ids=("ev-pump-101",)),
            TopologyNode("V-102", "vessel", confidence=0.96, evidence_ids=("ev-vessel-102",)),
        ),
        edges=(
            TopologyEdge(
                "P-101",
                "V-102",
                relationship="FLOWS_TO",
                confidence=0.88,
                evidence_ids=("ev-line-001",),
            ),
        ),
    )

    restored = TopologyResult.from_dict(result.to_dict())
    assert restored == result
    assert restored.to_dict()["edges"][0]["evidence_ids"] == ["ev-line-001"]


def test_topology_uncertainty_is_preserved_without_creating_an_edge():
    result = TopologyResult(
        document_id="synthetic-ambiguous-001",
        nodes=(
            TopologyNode("P-101", "pump", confidence=0.97),
            TopologyNode("V-102", "vessel", confidence=0.96),
        ),
        uncertainties=(
            {
                "source": "P-101",
                "target": "V-102",
                "reason": "crossing_vs_junction_ambiguous",
                "confidence": 0.62,
                "requires_verification": True,
            },
        ),
    )

    assert result.edges == ()
    assert result.to_dict()["uncertainties"][0]["requires_verification"] is True
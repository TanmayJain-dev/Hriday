import backend.intelligence.topology as topology
from backend.intelligence.topology.models import ExtractionResult, LineCandidate, Point
from backend.intelligence.topology.reconstruction import (
    DeterministicTopologyReconstructor,
    TopologyReconstructionConfig,
    reconstruct_topology,
)


CONFIG = TopologyReconstructionConfig(0.001, 0.001, 0.001)


def test_public_provider_entry_point_matches_functional_entry_point():
    extraction = ExtractionResult(
        "readiness-001",
        line_candidates=(
            LineCandidate("L-001", Point(0, 0), Point(5, 0), 0.8, evidence_ids=("ev-1",)),
        ),
    )

    expected = reconstruct_topology(extraction, CONFIG).to_dict()
    actual = DeterministicTopologyReconstructor(CONFIG).reconstruct(extraction).to_dict()
    assert actual == expected
    assert topology.TopologyProvider is not None


def test_public_exports_include_the_single_reconstruction_surface():
    assert "reconstruct_topology" in topology.__all__
    assert "DeterministicTopologyReconstructor" in topology.__all__
    assert topology.reconstruct_topology is reconstruct_topology


def test_invalid_configuration_and_required_ids_fail_at_public_boundary():
    invalid_values = (-0.1, float("inf"), float("nan"))
    for value in invalid_values:
        try:
            TopologyReconstructionConfig(value, 0.001, 0.001)
            assert False, "Expected invalid tolerance to fail"
        except ValueError:
            pass

    for extraction in (
        ExtractionResult(""),
        ExtractionResult("readiness-empty-id", line_candidates=(LineCandidate("", Point(0, 0), Point(1, 0), 0.8),)),
    ):
        try:
            reconstruct_topology(extraction, CONFIG)
            assert False, "Expected malformed required ID to fail"
        except ValueError:
            pass


def test_empty_input_is_valid_and_repeatable():
    extraction = ExtractionResult("readiness-empty")
    first = reconstruct_topology(extraction, CONFIG).to_dict()
    second = reconstruct_topology(extraction, CONFIG).to_dict()
    assert first == second == {
        "document_id": "readiness-empty",
        "nodes": [],
        "edges": [],
        "uncertainties": [],
    }
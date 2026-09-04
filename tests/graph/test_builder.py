"""Unit tests for GraphBuilder with fixture loading and uncertainty routing."""
import json
from pathlib import Path
from backend.intelligence.graph.builder import (
    build_graph,
    build_graph_with_uncertainties,
    build_graph_result,
)

ROOT = Path(__file__).resolve().parents[2]


def test_build_simple_pid_fixture():
    fixture_path = ROOT / "data/fixtures/simple_pid.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    store, uncertainties = build_graph_with_uncertainties(data)
    assert len(uncertainties) == 0
    assert len(store.all_nodes()) == 4
    assert len(store.all_edges()) == 3

    # Check downstream traversal
    downstream = store.downstream("P-101")
    assert ["P-101", "E-101"] in downstream
    assert ["P-101", "E-101", "V-102"] in downstream


def test_build_branching_pid_fixture():
    fixture_path = ROOT / "data/fixtures/branching_pid.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    store, uncertainties = build_graph_with_uncertainties(data)
    assert len(uncertainties) == 0
    assert len(store.all_nodes()) == 4
    assert len(store.all_edges()) == 3

    # E-101 branches to both V-102 and V-103
    downstream_p101 = store.downstream("P-101")
    assert ["P-101", "E-101", "V-102"] in downstream_p101
    assert ["P-101", "E-101", "V-103"] in downstream_p101


def test_build_ambiguous_junction_routes_to_uncertainties():
    """Non-negotiable rule: Uncertain/unverified connections must NOT become graph facts."""
    fixture_path = ROOT / "data/fixtures/ambiguous_junction.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    store, uncertainties = build_graph_with_uncertainties(data)

    # In ambiguous_junction.json, candidate_edge has requires_verification=true
    assert len(uncertainties) == 1
    assert uncertainties[0]["source"] == "P-101"
    assert uncertainties[0]["target"] == "V-104"
    assert uncertainties[0]["requires_verification"] is True

    # Graph store must NOT contain the ambiguous edge
    assert store.all_edges() == []
    assert store.paths_between("P-101", "V-104") == []


def test_confidence_threshold_gating():
    topology = {
        "document_id": "test-doc",
        "nodes": [{"id": "A", "type": "vessel"}, {"id": "B", "type": "pump"}],
        "edges": [
            {"source": "A", "target": "B", "confidence": 0.45, "relationship": "FLOWS_TO"}
        ],
    }
    # Default threshold is 0.70; 0.45 should be gated out into uncertainties
    store, uncertainties = build_graph_with_uncertainties(topology, confidence_threshold=0.70)
    assert len(store.all_edges()) == 0
    assert len(uncertainties) == 1
    assert uncertainties[0]["source"] == "A"
    assert uncertainties[0]["target"] == "B"


def test_build_graph_result_contract_conformance():
    fixture_path = ROOT / "data/fixtures/simple_pid.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    graph_result, uncertainties = build_graph_result(data, document_id="simple-001")
    d = graph_result.to_dict()
    assert d["document_id"] == "simple-001"
    assert "nodes" in d
    assert "edges" in d
    assert len(d["nodes"]) == 4
    assert len(d["edges"]) == 3


def test_missing_edge_confidence_routes_to_uncertainties():
    """Missing extraction/topology confidence must not silently become 1.0; routes to uncertainties."""
    topology = {
        "document_id": "test-doc-missing-conf",
        "nodes": [{"id": "P-101", "type": "pump"}, {"id": "V-101", "type": "vessel"}],
        "edges": [
            {"source": "P-101", "target": "V-101", "relationship": "FLOWS_TO"}
        ],
    }
    store, uncertainties = build_graph_with_uncertainties(topology)
    # The edge lacked confidence, so it must not be asserted as a confirmed fact
    assert len(store.all_edges()) == 0
    assert len(uncertainties) == 1
    assert uncertainties[0]["source"] == "P-101"
    assert uncertainties[0]["target"] == "V-101"
    assert uncertainties[0]["requires_verification"] is True
    assert uncertainties[0]["reason"] == "missing_confidence"


def test_confirmed_edge_without_evidence_routes_to_uncertainties():
    """Confirmed edge (high confidence) with empty evidence_ids must route to uncertainties."""
    topology = {
        "document_id": "test-doc-no-evidence",
        "nodes": [{"id": "P-101", "type": "pump"}, {"id": "V-101", "type": "vessel"}],
        "edges": [
            {
                "source": "P-101",
                "target": "V-101",
                "relationship": "FLOWS_TO",
                "confidence": 0.95,
                "evidence_ids": [],
            }
        ],
    }
    store, uncertainties = build_graph_with_uncertainties(topology)
    assert len(store.all_edges()) == 0
    assert len(uncertainties) == 1
    assert uncertainties[0]["source"] == "P-101"
    assert uncertainties[0]["target"] == "V-101"
    assert uncertainties[0]["requires_verification"] is True
    assert uncertainties[0]["reason"] == "missing_provenance"

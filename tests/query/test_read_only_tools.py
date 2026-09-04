"""Unit tests for agent-facing read-only graph tools."""
from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore
from backend.intelligence.query.read_only_tools import (
    downstream,
    downstream_detailed,
    get_node,
    neighbors,
    paths_between,
    paths_between_detailed,
    upstream,
    upstream_detailed,
)


def make_test_graph() -> NetworkXGraphStore:
    g = NetworkXGraphStore()
    g.add_node(GraphNode("V-101", "vessel", attributes={"role": "feed"}))
    g.add_node(GraphNode("P-101", "pump"))
    g.add_node(GraphNode("E-101", "exchanger"))
    g.add_node(GraphNode("V-102", "vessel", attributes={"role": "product"}))
    g.add_edge(GraphEdge("V-101", "P-101", "FLOWS_TO", confidence=0.98, evidence_ids=("ev-1",)))
    g.add_edge(GraphEdge("P-101", "E-101", "FLOWS_TO", confidence=0.94, evidence_ids=("ev-2",)))
    g.add_edge(GraphEdge("E-101", "V-102", "FLOWS_TO", confidence=0.91, evidence_ids=("ev-3",)))
    return g


def test_downstream_and_upstream_tools():
    g = make_test_graph()
    ds = downstream(g, "P-101")
    assert ["P-101", "E-101"] in ds
    assert ["P-101", "E-101", "V-102"] in ds

    us = upstream(g, "E-101")
    assert ["E-101", "P-101"] in us
    assert ["E-101", "P-101", "V-101"] in us


def test_paths_between_tool():
    g = make_test_graph()
    paths = paths_between(g, "V-101", "V-102")
    assert paths == [["V-101", "P-101", "E-101", "V-102"]]


def test_detailed_traversals():
    g = make_test_graph()
    detailed = downstream_detailed(g, "P-101")
    assert len(detailed) == 2
    # Check that each entry has path, confidence, evidence_ids
    for d in detailed:
        assert "path" in d
        assert "confidence" in d
        assert "evidence_ids" in d
        assert 0.0 <= d["confidence"] <= 1.0


def test_neighbors_and_get_node_tools():
    g = make_test_graph()
    nbrs = neighbors(g, "P-101")
    assert len(nbrs) == 1
    assert nbrs[0].id == "E-101"

    node = get_node(g, "V-101")
    assert node is not None
    assert node.type == "vessel"
    assert node.attributes["role"] == "feed"

    assert get_node(g, "NON-EXISTENT") is None

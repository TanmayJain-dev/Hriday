"""Unit tests for graph-level validation hooks."""
from backend.intelligence.graph.models import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore
from backend.intelligence.graph.validation import (
    validate_edge,
    validate_graph,
    validate_node,
)


def test_validate_node():
    valid = GraphNode("V-101", "vessel", confidence=0.95)
    assert validate_node(valid) == []

    empty_id = GraphNode("", "vessel")
    assert "empty_node_id" in validate_node(empty_id)

    bad_conf = GraphNode("V-102", "vessel", confidence=1.5)
    assert "confidence_out_of_range" in validate_node(bad_conf)


def test_validate_edge():
    valid = GraphEdge("A", "B", confidence=0.9, evidence_ids=("ev-1",))
    assert validate_edge(valid, require_provenance=True) == []

    missing_prov = GraphEdge("A", "B", confidence=0.9, evidence_ids=())
    assert "missing_provenance" in validate_edge(missing_prov, require_provenance=True)

    self_loop = GraphEdge("A", "A")
    assert "self_referential_edge" in validate_edge(self_loop)

    bad_conf = GraphEdge("A", "B", confidence=-0.1)
    assert "confidence_out_of_range" in validate_edge(bad_conf)


def test_validate_graph_detects_missing_endpoint():
    graph = NetworkXGraphStore()
    graph.add_node(GraphNode("A", "vessel"))
    # B is not added to nodes, but manually forced into _edges for testing
    graph._edges.append(GraphEdge("A", "B"))

    errors = validate_graph(graph)
    assert any("edge_target_missing_from_nodes:B" in err for err in errors)

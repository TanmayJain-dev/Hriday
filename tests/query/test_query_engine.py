"""Tests for the end-to-end QueryEngine orchestration."""
import pytest
from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore
from backend.intelligence.query.engine import QueryEngine
from backend.intelligence.query.local_adapter import LocalModelAdapter
from backend.intelligence.query.models import Answer


@pytest.fixture
def sample_graph() -> NetworkXGraphStore:
    """Builds an in-memory graph matching Member 1's GraphStore contract."""
    graph = NetworkXGraphStore()
    nodes = [
        GraphNode("V-101", "vessel", {"description": "Feed Drum"}, confidence=0.98),
        GraphNode("P-101", "pump", {"description": "Feed Pump"}, confidence=0.95),
        GraphNode("E-101", "exchanger", {"description": "Preheater"}, confidence=0.92),
        GraphNode("V-102", "vessel", {"description": "Product Vessel"}, confidence=0.96),
    ]
    for n in nodes:
        graph.add_node(n)

    edges = [
        GraphEdge("V-101", "P-101", "FLOWS_TO", confidence=0.98),
        GraphEdge("P-101", "E-101", "FLOWS_TO", confidence=0.94),
        GraphEdge("E-101", "V-102", "FLOWS_TO", confidence=0.96),
    ]
    for e in edges:
        graph.add_edge(e)
    return graph


def test_end_to_end_downstream_p101(sample_graph: NetworkXGraphStore):
    """Verifies the canonical MVP query: 'What is downstream of P-101?'"""
    engine = QueryEngine()
    result: Answer = engine.query("What is downstream of P-101?", sample_graph, document_id="demo-doc-001")

    # 1. Answer text is fact-grounded
    assert "Downstream of P-101" in result.answer
    assert "E-101" in result.answer
    assert "V-102" in result.answer
    assert "P-101 -> E-101" in result.answer

    # 2. GraphResult strictly mirrors retrieved subgraph facts
    graph_res = result.graph_result
    assert graph_res["document_id"] == "demo-doc-001"
    node_ids = {n["id"] for n in graph_res["nodes"]}
    assert node_ids == {"P-101", "E-101", "V-102"}
    assert ("V-101" not in node_ids)  # V-101 is upstream, must not be included

    edge_tuples = {(e["source"], e["target"]) for e in graph_res["edges"]}
    assert ("P-101", "E-101") in edge_tuples
    assert ("E-101", "V-102") in edge_tuples

    # 3. Evidence and verification adhere to contracts without fabrication
    assert isinstance(result.evidence, list)
    assert len(result.evidence) == 0  # Not fabricated
    assert result.verification["status"] == "not_required"
    assert 0.0 <= result.confidence <= 1.0


def test_end_to_end_upstream_query(sample_graph: NetworkXGraphStore):
    engine = QueryEngine()
    result = engine.query("What is upstream of V-102?", sample_graph)
    assert "Upstream of V-102" in result.answer
    assert "E-101" in result.answer
    assert "P-101" in result.answer
    assert "V-101" in result.answer


def test_query_layer_performs_no_graph_mutation(sample_graph: NetworkXGraphStore):
    """Guarantees the query layer strictly performs read-only operations."""
    engine = QueryEngine()

    # Capture initial state
    nodes_before = set(sample_graph._nodes.keys())
    edges_before = [(e.source, e.target, e.relationship) for e in sample_graph._edges]

    # Execute multiple diverse queries
    engine.query("What is downstream of P-101?", sample_graph)
    engine.query("What comes after pump 101?", sample_graph)
    engine.query("What is upstream of V-102?", sample_graph)
    engine.query("What is connected to P-101?", sample_graph)

    # State after must be identical
    nodes_after = set(sample_graph._nodes.keys())
    edges_after = [(e.source, e.target, e.relationship) for e in sample_graph._edges]

    assert nodes_before == nodes_after
    assert edges_before == edges_after


def test_query_non_existent_entity(sample_graph: NetworkXGraphStore):
    """Non-existent entity returns truthful absence of facts without error."""
    engine = QueryEngine()
    result = engine.query("What is downstream of P-999?", sample_graph)
    assert "No downstream equipment found connected to P-999" in result.answer
    assert len(result.graph_result["nodes"]) == 1
    assert result.graph_result["nodes"][0]["id"] == "P-999"
    assert len(result.graph_result["edges"]) == 0


def test_local_model_adapter_offline():
    """Confirms local model adapter functions without cloud keys or dependencies."""
    adapter = LocalModelAdapter()
    with pytest.raises(RuntimeError, match="No local inference engine configured"):
        adapter.generate("test prompt")

    custom_adapter = LocalModelAdapter(inference_fn=lambda p: "Mock local response")
    assert custom_adapter.generate("Hello") == "Mock local response"

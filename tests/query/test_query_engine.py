"""Tests for the end-to-end QueryEngine orchestration."""
from __future__ import annotations
from contextlib import contextmanager
import re

from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore
from backend.intelligence.query.engine import QueryEngine
from backend.intelligence.query.local_adapter import LocalModelAdapter
from backend.intelligence.query.models import Answer


@contextmanager
def assert_raises(exc_type: type[Exception], match: str | None = None):
    try:
        yield
    except exc_type as ex:
        if match:
            assert re.search(match, str(ex)), f"Expected match {match!r}, got {ex!r}"
        return
    raise AssertionError(f"Expected {exc_type.__name__} was not raised")


def make_sample_graph() -> NetworkXGraphStore:
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


def test_end_to_end_downstream_p101():
    """Verifies the canonical MVP query: 'What is downstream of P-101?'"""
    sample_graph = make_sample_graph()
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


def test_end_to_end_upstream_query():
    sample_graph = make_sample_graph()
    engine = QueryEngine()
    result = engine.query("What is upstream of V-102?", sample_graph)
    assert "Upstream of V-102" in result.answer
    assert "E-101" in result.answer
    assert "P-101" in result.answer
    assert "V-101" in result.answer


def test_query_layer_performs_no_graph_mutation():
    """Guarantees the query layer strictly performs read-only operations."""
    sample_graph = make_sample_graph()
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


def test_query_non_existent_entity():
    """Non-existent entity returns truthful absence of facts without error."""
    sample_graph = make_sample_graph()
    engine = QueryEngine()
    result = engine.query("What is downstream of P-999?", sample_graph)
    assert "No downstream equipment found connected to P-999" in result.answer
    assert len(result.graph_result["nodes"]) == 1
    assert result.graph_result["nodes"][0]["id"] == "P-999"
    assert len(result.graph_result["edges"]) == 0


def test_local_model_adapter_offline():
    """Confirms local model adapter functions without cloud keys or dependencies."""
    adapter = LocalModelAdapter()
    with assert_raises(RuntimeError, match="No local inference engine configured"):
        adapter.generate("test prompt")

    custom_adapter = LocalModelAdapter(inference_fn=lambda p: "Mock local response")
    assert custom_adapter.generate("Hello") == "Mock local response"


def test_high_confidence_result_does_not_require_verification():
    sample_graph = make_sample_graph()
    engine = QueryEngine()

    result = engine.query("What is downstream of P-101?", sample_graph)

    assert result.confidence >= 0.9
    assert result.verification["status"] == "not_required"


def test_unknown_entity_preserves_uncertainty():
    sample_graph = make_sample_graph()
    engine = QueryEngine()

    result = engine.query("What is downstream of P-999?", sample_graph)

    assert result.confidence < 1.0
    assert result.verification["status"] != "not_required"
    assert result.graph_result["nodes"][0]["id"] == "P-999"


def test_confidence_is_not_artificially_increased():
    sample_graph = make_sample_graph()
    engine = QueryEngine()

    result = engine.query("What is downstream of P-101?", sample_graph)

    # The weakest known node/edge in the returned path is below 1.0.
    # The query layer must never turn graph uncertainty into 1.0 confidence.
    assert result.confidence < 1.0


def test_low_confidence_result_requires_verification():
    engine = QueryEngine()

    # Temporarily introduce a weak graph fact for this query.
    weak_graph = NetworkXGraphStore()
    weak_graph.add_node(
        GraphNode("P-200", "pump", {"description": "Weak-confidence pump"}, confidence=0.60)
    )
    weak_graph.add_node(
        GraphNode("E-200", "exchanger", {"description": "Weak-confidence exchanger"}, confidence=0.95)
    )
    weak_graph.add_edge(
        GraphEdge("P-200", "E-200", "FLOWS_TO", confidence=0.55)
    )

    result = engine.query("What is downstream of P-200?", weak_graph)

    assert result.confidence < 0.9
    assert result.verification["status"] != "not_required"


def test_weak_edge_in_middle_lowers_confidence():
    """Verifies Audit 2: A --0.95--> B --0.72--> C yields conservative confidence 0.72."""
    class GraphWithEdgeConfidence(NetworkXGraphStore):
        def __init__(self):
            super().__init__()
            self._edge_map: dict[tuple[str, str], GraphEdge] = {}

        def add_edge(self, edge: GraphEdge) -> None:
            super().add_edge(edge)
            self._edge_map[(edge.source, edge.target)] = edge

        def get_edge(self, source: str, target: str) -> GraphEdge | None:
            return self._edge_map.get((source, target))

    graph = GraphWithEdgeConfidence()
    graph.add_node(GraphNode("A-100", "pump", confidence=0.95))
    graph.add_node(GraphNode("B-100", "exchanger", confidence=0.95))
    graph.add_node(GraphNode("C-100", "vessel", confidence=0.95))
    graph.add_edge(GraphEdge("A-100", "B-100", "FLOWS_TO", confidence=0.95))
    graph.add_edge(GraphEdge("B-100", "C-100", "FLOWS_TO", confidence=0.72))

    engine = QueryEngine()
    result = engine.query("What is downstream of A-100?", graph)

    assert result.confidence == 0.72
    assert result.verification["status"] == "required"
    assert result.verification["reason"] == "low_confidence"


def test_weak_node_in_middle_lowers_confidence():
    """Verifies Audit 2: Path with weak node A (0.95) -> B (0.65) -> C (0.92) conservatively yields 0.65."""
    graph = NetworkXGraphStore()
    graph.add_node(GraphNode("A-101", "pump", confidence=0.95))
    graph.add_node(GraphNode("B-101", "exchanger", confidence=0.65))
    graph.add_node(GraphNode("C-101", "vessel", confidence=0.92))
    graph.add_edge(GraphEdge("A-101", "B-101", "FLOWS_TO"))
    graph.add_edge(GraphEdge("B-101", "C-101", "FLOWS_TO"))

    engine = QueryEngine()
    result = engine.query("What is downstream of A-101?", graph)

    assert result.confidence == 0.65
    assert result.verification["status"] == "required"


def test_missing_confidence_handled_conservatively():
    """Verifies Audit 2: Missing or None confidence is conservatively treated as 0.0."""
    class CustomNode:
        def __init__(self, id: str, type: str):
            self.id = id
            self.type = type
            self.attributes = {}
            self.confidence = None  # Missing confidence

    class GraphWithNoneConfidence(NetworkXGraphStore):
        def get_node(self, node_id: str):
            if node_id == "P-500":
                return CustomNode("P-500", "pump")
            return super().get_node(node_id)

    graph = GraphWithNoneConfidence()
    graph.add_node(GraphNode("P-500", "pump"))

    engine = QueryEngine()
    result = engine.query("What is downstream of P-500?", graph)

    assert result.confidence == 0.0
    assert result.verification["status"] == "required"


def test_empty_graph_query_fails_safely():
    """Verifies Audit 11: Query against completely empty graph handles uncertainty safely."""
    empty_graph = NetworkXGraphStore()
    engine = QueryEngine()

    result = engine.query("What is downstream of P-101?", empty_graph)

    assert result.confidence == 0.0
    assert result.verification["status"] == "required"
    assert "No downstream equipment found" in result.answer


def test_traversal_direction_semantics():
    """Verifies Audit 8: Downstream and upstream relationships preserve physical flow direction."""
    sample_graph = make_sample_graph()
    engine = QueryEngine()

    # Downstream from P-101 -> E-101 -> V-102
    downstream_result = engine.query("What is downstream of P-101?", sample_graph)
    downstream_edges = [(e["source"], e["target"]) for e in downstream_result.graph_result["edges"]]
    assert ("P-101", "E-101") in downstream_edges
    assert ("E-101", "V-102") in downstream_edges

    # Upstream from V-102 should produce physical flow: E-101 -> V-102 and P-101 -> E-101
    upstream_result = engine.query("What is upstream of V-102?", sample_graph)
    upstream_edges = [(e["source"], e["target"]) for e in upstream_result.graph_result["edges"]]
    assert ("E-101", "V-102") in upstream_edges
    assert ("P-101", "E-101") in upstream_edges
    # Must NOT have reversed edges (V-102 -> E-101)
    assert ("V-102", "E-101") not in upstream_edges


def test_neighbors_query_semantics():
    """Verifies Audit 6 & 8: Neighbors intent queries connected equipment with physical relationship."""
    sample_graph = make_sample_graph()
    engine = QueryEngine()
    result = engine.query("What is connected to P-101?", sample_graph)

    assert "Directly connected to P-101: E-101" in result.answer
    assert any(e["source"] == "P-101" and e["target"] == "E-101" for e in result.graph_result["edges"])
    assert result.graph_result["edges"][0]["relationship"] == "FLOWS_TO"


def test_canonical_graph_path_consumption_and_provenance():
    """Verifies Audit 1, 2 & 3: Consumes canonical GraphPath, weakest-link confidence, and evidence provenance."""
    from backend.intelligence.graph.models import GraphPath

    class CanonicalGraphStoreMock:
        def __init__(self):
            self.nodes_dict = {
                "P-101": GraphNode("P-101", "pump", confidence=0.98),
                "E-101": GraphNode("E-101", "exchanger", confidence=0.95),
                "V-102": GraphNode("V-102", "vessel", confidence=0.96),
            }
            self.edge1 = GraphEdge("P-101", "E-101", "FLOWS_TO", confidence=0.94, evidence_ids=("ev-101",))
            self.edge2 = GraphEdge("E-101", "V-102", "FLOWS_TO", confidence=0.78, evidence_ids=("ev-102", "ev-103"))

        def get_node(self, node_id: str):
            return self.nodes_dict.get(node_id)

        def get_edge(self, source: str, target: str, relationship: str | None = None):
            for e in (self.edge1, self.edge2):
                if e.source == source and e.target == target:
                    if relationship is None or e.relationship == relationship:
                        return e
            return None

        def downstream_paths(self, node_id: str, max_depth: int | None = None):
            if node_id == "P-101":
                p1 = GraphPath(nodes=("P-101", "E-101"), edges=(self.edge1,))
                p2 = GraphPath(nodes=("P-101", "E-101", "V-102"), edges=(self.edge1, self.edge2))
                return [p1, p2]
            return []

        def paths_between_detailed(self, source: str, target: str, max_depth: int | None = None):
            if source == "P-101" and target == "V-102":
                p = GraphPath(nodes=("P-101", "E-101", "V-102"), edges=(self.edge1, self.edge2))
                return [p]
            return []

    graph = CanonicalGraphStoreMock()
    engine = QueryEngine()

    # 1. Downstream query directly consuming GraphPath
    res = engine.query("What is downstream of P-101?", graph)
    assert res.confidence == 0.78  # Weakest link across graph nodes & canonical path edges
    assert res.verification["status"] == "required"
    assert res.verification["reason"] == "low_confidence"
    assert "ev-101" in res.evidence
    assert "ev-102" in res.evidence
    assert "ev-103" in res.evidence

    # Edge provenance preserved
    edge_entries = res.graph_result["edges"]
    assert any(e["source"] == "P-101" and e["target"] == "E-101" and e["confidence"] == 0.94 for e in edge_entries)
    assert any(e["source"] == "E-101" and e["target"] == "V-102" and e["confidence"] == 0.78 for e in edge_entries)


def test_paths_between_valid_path():
    """Verifies Audit 6: PATHS_BETWEEN between two known connected entities."""
    class GraphWithPaths(NetworkXGraphStore):
        def paths_between(self, source: str, target: str, max_depth: int | None = None):
            if source == "P-101" and target == "V-102":
                return [["P-101", "E-101", "V-102"]]
            return []

    g = GraphWithPaths()
    g.add_node(GraphNode("P-101", "pump", confidence=0.96))
    g.add_node(GraphNode("E-101", "exchanger", confidence=0.95))
    g.add_node(GraphNode("V-102", "vessel", confidence=0.94))
    g.add_edge(GraphEdge("P-101", "E-101", "FLOWS_TO", confidence=0.95))
    g.add_edge(GraphEdge("E-101", "V-102", "FLOWS_TO", confidence=0.93))

    engine = QueryEngine()
    result = engine.query("What is the path between P-101 and V-102?", g)

    assert "Path from P-101 to V-102: P-101 -> E-101 -> V-102" in result.answer
    assert result.confidence >= 0.90
    assert result.verification["status"] == "not_required"
    assert len(result.graph_result["edges"]) == 2


def test_paths_between_no_path():
    """Verifies Audit 6: Disconnected entities yield clear unsupported explanation without fabricated edges."""
    class GraphNoPath(NetworkXGraphStore):
        def paths_between(self, source: str, target: str, max_depth: int | None = None):
            return []

    g = GraphNoPath()
    g.add_node(GraphNode("P-101", "pump", confidence=0.95))
    g.add_node(GraphNode("TK-900", "tank", confidence=0.95))

    engine = QueryEngine()
    result = engine.query("What is the path between P-101 and TK-900?", g)

    assert "No directed path found connecting P-101 to TK-900" in result.answer
    assert len(result.graph_result["edges"]) == 0


def test_paths_between_unknown_source_and_target():
    """Verifies Audit 5 & 6: Unknown entities in paths-between remain uncertain with confidence 0.0."""
    g = NetworkXGraphStore()
    g.add_node(GraphNode("P-101", "pump", confidence=0.95))

    engine = QueryEngine()

    # Unknown source
    res_unknown_src = engine.query("What is the path between X-999 and P-101?", g)
    assert res_unknown_src.confidence == 0.0
    assert res_unknown_src.verification["status"] == "required"
    assert any(n["id"] == "X-999" and n["type"] == "unknown" for n in res_unknown_src.graph_result["nodes"])

    # Unknown target
    res_unknown_tgt = engine.query("What is the path between P-101 and Y-999?", g)
    assert res_unknown_tgt.confidence == 0.0
    assert res_unknown_tgt.verification["status"] == "required"
    assert any(n["id"] == "Y-999" and n["type"] == "unknown" for n in res_unknown_tgt.graph_result["nodes"])

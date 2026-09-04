"""Unit tests for canonical graph models."""
from backend.intelligence.graph.models import GraphEdge, GraphNode, GraphPath, GraphResult


def test_graph_node_to_and_from_dict():
    node = GraphNode(
        id="V-101",
        type="vessel",
        attributes={"service": "crude", "design_pressure": 15.5},
        confidence=0.99,
        evidence_ids=("ev-001", "ev-002"),
    )
    d = node.to_dict()
    assert d["id"] == "V-101"
    assert d["type"] == "vessel"
    assert d["confidence"] == 0.99
    assert d["attributes"]["service"] == "crude"
    assert d["evidence_ids"] == ["ev-001", "ev-002"]

    restored = GraphNode.from_dict(d)
    assert restored.id == node.id
    assert restored.type == node.type
    assert restored.confidence == node.confidence
    assert restored.evidence_ids == ("ev-001", "ev-002")


def test_graph_edge_to_and_from_dict():
    edge = GraphEdge(
        source="P-101",
        target="E-101",
        relationship="FLOWS_TO",
        attributes={"line_size": "6-inch"},
        confidence=0.95,
        evidence_ids=("ev-101",),
    )
    d = edge.to_dict()
    assert d["source"] == "P-101"
    assert d["target"] == "E-101"
    assert d["relationship"] == "FLOWS_TO"
    assert d["confidence"] == 0.95
    assert d["attributes"]["line_size"] == "6-inch"
    assert d["evidence_ids"] == ["ev-101"]

    restored = GraphEdge.from_dict(d)
    assert restored.source == edge.source
    assert restored.target == edge.target
    assert restored.confidence == edge.confidence


def test_graph_path_confidence_and_evidence_propagation():
    e1 = GraphEdge("P-101", "E-101", confidence=0.95, evidence_ids=("ev-1",))
    e2 = GraphEdge("E-101", "V-102", confidence=0.88, evidence_ids=("ev-2", "ev-3"))
    path = GraphPath(nodes=("P-101", "E-101", "V-102"), edges=(e1, e2))

    # Path confidence should degrade to the minimum confidence along the path
    assert path.confidence == 0.88
    # Provenance should aggregate all evidence IDs without duplicates
    assert path.evidence_ids == ("ev-1", "ev-2", "ev-3")
    assert path.to_string() == "P-101 -> E-101 -> V-102"

    d = path.to_dict()
    assert d["path"] == ["P-101", "E-101", "V-102"]
    assert d["confidence"] == 0.88
    assert d["evidence_ids"] == ["ev-1", "ev-2", "ev-3"]
    assert d["edge_count"] == 2


def test_graph_result_schema_conformance():
    res = GraphResult(
        document_id="pid-test-01",
        nodes=[{"id": "P-101", "type": "pump"}],
        edges=[{"source": "P-101", "target": "E-101", "relationship": "FLOWS_TO"}],
    )
    d = res.to_dict()
    assert d["document_id"] == "pid-test-01"
    assert len(d["nodes"]) == 1
    assert len(d["edges"]) == 1
    restored = GraphResult.from_dict(d)
    assert restored.document_id == res.document_id

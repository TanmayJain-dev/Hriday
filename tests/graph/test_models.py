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


def test_graph_path_default_confidence_with_edges():
    """Default confidence (1.0) must drop to weakest edge."""
    e1 = GraphEdge("A", "B", confidence=0.92, evidence_ids=("ev-1",))
    e2 = GraphEdge("B", "C", confidence=0.74, evidence_ids=("ev-2",))
    path = GraphPath(nodes=("A", "B", "C"), edges=(e1, e2))
    assert path.confidence == 0.74


def test_graph_path_explicit_confidence_higher_than_weakest_edge_is_capped():
    """Explicit confidence higher than weakest edge must be capped at weakest edge."""
    e1 = GraphEdge("A", "B", confidence=0.95, evidence_ids=("ev-1",))
    e2 = GraphEdge("B", "C", confidence=0.60, evidence_ids=("ev-2",))
    # User tries to assert 0.95 confidence on a path with a 0.60 edge
    path = GraphPath(nodes=("A", "B", "C"), edges=(e1, e2), confidence=0.95)
    assert path.confidence == 0.60


def test_graph_path_explicit_confidence_lower_than_weakest_edge_is_preserved():
    """Explicit confidence lower than weakest edge must not be upgraded."""
    e1 = GraphEdge("A", "B", confidence=0.95, evidence_ids=("ev-1",))
    e2 = GraphEdge("B", "C", confidence=0.90, evidence_ids=("ev-2",))
    # Prior or external uncertainty lowered path to 0.50
    path = GraphPath(nodes=("A", "B", "C"), edges=(e1, e2), confidence=0.50)
    assert path.confidence == 0.50


def test_graph_path_multi_edge_weakest_link_and_provenance():
    """Multi-edge path respects weakest link and preserves ordered, deduplicated provenance."""
    e1 = GraphEdge("A", "B", confidence=0.99, evidence_ids=("ev-1", "ev-shared"))
    e2 = GraphEdge("B", "C", confidence=0.33, evidence_ids=("ev-2", "ev-shared"))
    e3 = GraphEdge("C", "D", confidence=0.85, evidence_ids=("ev-3",))
    path = GraphPath(nodes=("A", "B", "C", "D"), edges=(e1, e2, e3))
    assert path.confidence == 0.33
    assert path.evidence_ids == ("ev-1", "ev-shared", "ev-2", "ev-3")
    assert path.to_string() == "A -> B -> C -> D"


def test_graph_path_no_edges_retains_assigned_confidence():
    """Single-node or 0-edge path retains its assigned confidence."""
    path = GraphPath(nodes=("A",), edges=(), confidence=0.85)
    assert path.confidence == 0.85
    assert path.evidence_ids == ()


def test_graph_path_explicit_evidence_always_includes_edge_evidence():
    """Hardened provenance: edge evidence is always included even if caller supplies evidence_ids."""
    e1 = GraphEdge("A", "B", confidence=0.90, evidence_ids=("edge-ev-1",))
    e2 = GraphEdge("B", "C", confidence=0.85, evidence_ids=("edge-ev-2",))
    path = GraphPath(
        nodes=("A", "B", "C"),
        edges=(e1, e2),
        evidence_ids=("initial-ev-0",),
    )
    # Both initial and edge evidence must be present, deduplicated, and in order
    assert path.evidence_ids == ("initial-ev-0", "edge-ev-1", "edge-ev-2")


def test_graph_models_eliminate_silent_one_dot_zero_confidence_defaults():
    """Missing confidence in dictionary serialization must never silently default to 1.0."""
    try:
        GraphEdge.from_dict({"source": "A", "target": "B"})
        assert False, "Expected ValueError when confidence is omitted from serialized edge data"
    except ValueError as ex:
        assert "requires explicit 'confidence'" in str(ex)

    valid_edge = GraphEdge.from_dict({"source": "A", "target": "B", "confidence": 0.75})
    assert valid_edge.confidence == 0.75

    node = GraphNode.from_dict({"id": "V-100", "type": "vessel"})
    assert node.confidence is None


def test_graph_edge_constructor_requires_explicit_confidence():
    """GraphEdge constructor must require explicit confidence and reject None or omitted confidence."""
    try:
        GraphEdge("A", "B")  # type: ignore[call-arg]
        assert False, "Expected ValueError when confidence is omitted in GraphEdge"
    except ValueError as ex:
        assert "requires explicit confidence" in str(ex)

    try:
        GraphEdge("A", "B", confidence=None)
        assert False, "Expected ValueError when confidence is None in GraphEdge"
    except ValueError as ex:
        assert "requires explicit confidence" in str(ex)

    edge = GraphEdge("A", "B", confidence=0.88)
    assert edge.confidence == 0.88


def test_graph_edge_positional_parameter_order_and_confidence():
    """GraphEdge must preserve original positional ordering:
    source, target, relationship, attributes, confidence, evidence_ids
    while still enforcing that confidence is explicitly provided."""
    # 1. Full positional construction with original argument ordering
    edge = GraphEdge(
        "P-101",
        "E-101",
        "FLOWS_TO",
        {"line_size": "6-inch"},
        0.95,
        ("ev-101",),
    )
    assert edge.source == "P-101"
    assert edge.target == "E-101"
    assert edge.relationship == "FLOWS_TO"
    assert edge.attributes == {"line_size": "6-inch"}
    assert edge.confidence == 0.95
    assert edge.evidence_ids == ("ev-101",)

    # 2. Positional construction up to attributes (omitting confidence -> None) raises ValueError
    try:
        GraphEdge("P-101", "E-101", "FLOWS_TO", {"line_size": "6-inch"})  # type: ignore[call-arg]
        assert False, "Expected ValueError when positional confidence is omitted"
    except ValueError as ex:
        assert "requires explicit confidence" in str(ex)

    # 3. Explicit positional None confidence raises ValueError
    try:
        GraphEdge("P-101", "E-101", "FLOWS_TO", {"line_size": "6-inch"}, None)  # type: ignore[arg-type]
        assert False, "Expected ValueError when positional confidence is None"
    except ValueError as ex:
        assert "requires explicit confidence" in str(ex)

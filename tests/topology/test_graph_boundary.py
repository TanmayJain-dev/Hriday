from backend.intelligence.graph.builder import build_graph_with_uncertainties


def topology_result(**overrides):
    result = {
        "document_id": "synthetic-boundary-001",
        "nodes": [
            {"id": "P-101", "type": "pump", "confidence": 0.91, "evidence_ids": ["ev-p"]},
            {"id": "L-001", "type": "line", "confidence": 0.88, "evidence_ids": ["ev-l"]},
        ],
        "edges": [
            {
                "source": "P-101",
                "target": "L-001",
                "relationship": "CONNECTED_TO",
                "confidence": 0.88,
                "evidence_ids": ["ev-p", "ev-l"],
                "attributes": {"line_endpoint": "start", "distance": 0.0},
            }
        ],
        "uncertainties": [],
    }
    result.update(overrides)
    return result


def test_topology_nodes_and_edges_reach_graph_with_metadata_intact():
    store, uncertainties = build_graph_with_uncertainties(topology_result())

    assert uncertainties == []
    assert {node.id for node in store.all_nodes()} == {"P-101", "L-001"}
    edge = store.get_edge("P-101", "L-001")
    assert edge is not None
    assert edge.confidence == 0.88
    assert edge.evidence_ids == ("ev-p", "ev-l")
    assert edge.attributes == {"line_endpoint": "start", "distance": 0.0}


def test_topology_edge_reason_and_review_state_are_preserved_as_uncertainty():
    topology = topology_result(
        edges=[
            {
                "source": "P-101",
                "target": "L-001",
                "relationship": "CONNECTED_TO",
                "confidence": 0.62,
                "evidence_ids": ["ev-p", "ev-l"],
                "requires_verification": True,
                "reason": "ambiguous_crossing",
                "attributes": {"intersection": {"x": 5, "y": 5}},
            }
        ]
    )

    store, uncertainties = build_graph_with_uncertainties(topology)
    assert store.all_edges() == []
    assert uncertainties[0]["requires_verification"] is True
    assert uncertainties[0]["reason"] == "ambiguous_crossing"
    assert uncertainties[0]["evidence_ids"] == ["ev-p", "ev-l"]
    assert uncertainties[0]["attributes"] == {"intersection": {"x": 5, "y": 5}}


def test_missing_provenance_is_blocked_at_graph_boundary():
    topology = topology_result(
        edges=[
            {
                "source": "P-101",
                "target": "L-001",
                "relationship": "CONNECTED_TO",
                "confidence": 0.88,
                "evidence_ids": [],
            }
        ]
    )

    store, uncertainties = build_graph_with_uncertainties(topology)
    assert store.all_edges() == []
    assert uncertainties[0]["reason"] == "missing_provenance"
    assert uncertainties[0]["requires_verification"] is True


def test_missing_endpoint_uncertainty_preserves_topology_metadata():
    topology = topology_result(
        nodes=[{"id": "P-101", "type": "pump", "confidence": 0.91}],
        edges=[
            {
                "source": "P-101",
                "target": "L-MISSING",
                "confidence": 0.8,
                "evidence_ids": ["ev-edge"],
                "reason": "unresolved_endpoint",
                "attributes": {"line_endpoint": "start"},
            }
        ],
    )

    store, uncertainties = build_graph_with_uncertainties(topology)
    assert store.all_edges() == []
    assert uncertainties[0]["reason"] == "missing_endpoint_node"
    assert uncertainties[0]["evidence_ids"] == ["ev-edge"]
    assert uncertainties[0]["attributes"] == {"line_endpoint": "start"}


def test_duplicate_edges_are_not_duplicated_by_graph_store_conversion():
    topology = topology_result(
        edges=[
            topology_result()["edges"][0],
            topology_result()["edges"][0],
        ]
    )

    store, uncertainties = build_graph_with_uncertainties(topology)
    assert uncertainties == []
    assert len(store.all_edges()) == 1


def test_non_connected_crossing_uncertainty_does_not_create_graph_edge():
    topology = topology_result(
        uncertainties=[
            {
                "line_ids": ["L-001", "L-002"],
                "kind": "non_connected_crossing",
                "reason": "interior_intersection_without_junction_evidence",
                "requires_verification": False,
                "confidence": 0.7,
                "evidence_ids": ["ev-l1", "ev-l2"],
            }
        ],
        edges=[],
    )

    store, uncertainties = build_graph_with_uncertainties(topology)
    assert store.all_edges() == []
    assert uncertainties[0]["kind"] == "non_connected_crossing"


def test_graph_conversion_is_deterministic_and_empty_result_is_supported():
    empty = {"document_id": "empty", "nodes": [], "edges": [], "uncertainties": []}
    first_store, first_uncertainties = build_graph_with_uncertainties(empty)
    second_store, second_uncertainties = build_graph_with_uncertainties(empty)
    assert first_store.to_dict("empty") == second_store.to_dict("empty")
    assert first_uncertainties == second_uncertainties == []


def test_graph_edge_model_round_trips_reason_and_review_state():
    # Test 1: Confirmed edges (requires_verification=False) reach the graph without topology metadata
    confirmed_topology = topology_result(
        edges=[
            {
                **topology_result()["edges"][0],
                "reason": "documented_rule",
                "requires_verification": False,
            }
        ]
    )
    store, _ = build_graph_with_uncertainties(confirmed_topology)
    edge = store.get_edge("P-101", "L-001")
    assert edge is not None
    # GraphEdge no longer stores reason/requires_verification; these are topology/uncertainties concerns
    assert not hasattr(edge, 'reason') or edge.reason is None
    assert not hasattr(edge, 'requires_verification') or edge.requires_verification is False
    # Verify the graph serialization does not include these topology-specific fields
    edge_dict = store.to_dict("synthetic-boundary-001")["edges"][0]
    assert "reason" not in edge_dict or edge_dict.get("reason") is None
    
    # Test 2: Unconfirmed edges (requires_verification=True) route to uncertainties with metadata preserved
    uncertain_topology = topology_result(
        edges=[
            {
                **topology_result()["edges"][0],
                "reason": "documented_rule",
                "requires_verification": True,
            }
        ]
    )
    store2, uncertainties = build_graph_with_uncertainties(uncertain_topology)
    assert store2.all_edges() == []
    assert uncertainties[0]["reason"] == "documented_rule"
    assert uncertainties[0]["requires_verification"] is True
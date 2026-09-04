"""Integration tests for the thin FastAPI entry point."""
from unittest.mock import MagicMock
from backend.intelligence.graph.networkx_store import NetworkXGraphStore


def test_api_query_delegation():
    try:
        import fastapi
    except ImportError:
        # FastAPI not installed in current environment; skip gracefully
        return

    from fastapi.testclient import TestClient
    from backend.api.main import app, set_graph_provider, _orchestrator

    client = TestClient(app)

    # Setup mock query engine on orchestrator
    mock_engine = MagicMock()
    mock_engine.query.return_value = {
        "answer": "Downstream of P-101 is E-101",
        "confidence": 0.95,
        "graph_result": {"document_id": "test-pid", "nodes": [], "edges": []},
        "evidence": [],
        "verification": {"status": "not_required"},
    }
    _orchestrator.query_engine = mock_engine

    # Case 1: No graph provider configured
    set_graph_provider(None)
    res = client.post("/api/query", json={"question": "What is downstream of P-101?"})
    assert res.status_code == 503

    # Case 2: Graph provider configured and resolves graph
    sample_graph = NetworkXGraphStore()
    set_graph_provider(lambda doc_id: sample_graph if doc_id == "test-pid" else None)

    res = client.post(
        "/api/query",
        json={"question": "What is downstream of P-101?", "document_id": "test-pid"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["answer"] == "Downstream of P-101 is E-101"
    assert data["confidence"] == 0.95

    # Case 3: Unknown document ID returns 404
    res_404 = client.post(
        "/api/query",
        json={"question": "What is downstream of P-101?", "document_id": "unknown"},
    )
    assert res_404.status_code == 404

    # Case 4: Empty question returns 400
    res_400 = client.post("/api/query", json={"question": "   "})
    assert res_400.status_code == 400

    # Reset provider
    set_graph_provider(None)

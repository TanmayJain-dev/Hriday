"""End-to-end integration tests for backend API, orchestration, and query engine."""
from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app, get_document_graph, set_document_graph
from backend.intelligence.graph.builder import build_graph
from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore
from backend.orchestration.pipeline import Pipeline, QueryOrchestrator


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def answer_schema() -> dict:
    root = Path(__file__).resolve().parents[2]
    return json.loads((root / "contracts" / "answer.schema.json").read_text(encoding="utf-8"))


def test_api_health(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "hriday-api"}


def test_end_to_end_api_mvp_query(client: TestClient, answer_schema: dict):
    """Verifies full stack execution of the canonical MVP query:
    'What is downstream of P-101?' through FastAPI -> Orchestrator -> QueryEngine -> GraphStore.
    """
    response = client.post(
        "/api/query",
        json={"question": "What is downstream of P-101?", "document_id": "demo-simple-001"},
    )
    assert response.status_code == 200
    data = response.json()

    # 1. Verify all required keys from contracts/answer.schema.json are present
    for req_key in answer_schema["required"]:
        assert req_key in data, f"Missing required contract field: {req_key}"

    # 2. Verify answer text is fact-grounded
    answer_text = data["answer"]
    assert "Downstream of P-101" in answer_text
    assert "E-101" in answer_text
    assert "V-102" in answer_text
    assert "P-101 -> E-101" in answer_text

    # 3. Verify graph_result contains correct nodes and edges without fabricating
    graph_res = data["graph_result"]
    assert graph_res["document_id"] == "demo-simple-001"
    node_ids = {n["id"] for n in graph_res["nodes"]}
    assert node_ids == {"P-101", "E-101", "V-102"}
    assert "V-101" not in node_ids  # V-101 is upstream, must not be included

    edge_tuples = {(e["source"], e["target"]) for e in graph_res["edges"]}
    assert ("P-101", "E-101") in edge_tuples
    assert ("E-101", "V-102") in edge_tuples

    # 4. Verify confidence and evidence
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["evidence"], list)
    assert len(data["evidence"]) == 0
    assert data["verification"]["status"] == "not_required"


def test_end_to_end_api_upstream_query(client: TestClient):
    response = client.post(
        "/api/query",
        json={"question": "What is upstream of V-102?", "document_id": "demo-simple-001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Upstream of V-102" in data["answer"]
    assert "E-101" in data["answer"]
    assert "P-101" in data["answer"]
    assert "V-101" in data["answer"]


def test_end_to_end_orchestrator_direct():
    """Verifies direct orchestration invocation with a custom graph fixture."""
    graph = NetworkXGraphStore()
    graph.add_node(GraphNode("P-101", "pump", confidence=0.99))
    graph.add_node(GraphNode("V-101", "vessel", confidence=0.95))
    graph.add_edge(GraphEdge("P-101", "V-101", "FLOWS_TO", confidence=0.97))

    orchestrator = QueryOrchestrator()
    answer = orchestrator.execute_query("What is downstream of P-101?", graph, document_id="test-doc")

    assert "Downstream of P-101: V-101" in answer.answer
    assert answer.graph_result["document_id"] == "test-doc"
    assert answer.confidence == 0.97


def test_pipeline_query_convenience_method():
    """Verifies Pipeline.query integration hook."""
    graph = NetworkXGraphStore()
    graph.add_node(GraphNode("P-101", "pump"))
    graph.add_node(GraphNode("E-101", "exchanger"))
    graph.add_edge(GraphEdge("P-101", "E-101", "FLOWS_TO"))

    pipeline = Pipeline(ingestion=None, extraction=None, topology=None, graph_builder=None)
    answer = pipeline.query(graph, "What is downstream of P-101?", document_id="doc-pipe")

    assert "Downstream of P-101: E-101" in answer.answer
    assert answer.graph_result["document_id"] == "doc-pipe"


def test_api_query_unsupported_intent_fails_safely(client: TestClient):
    response = client.post(
        "/api/query",
        json={"question": "What is the cost of pump 101?", "document_id": "demo-simple-001"},
    )
    assert response.status_code == 400
    assert "Could not determine a supported query intent" in response.json()["detail"]


def test_api_query_empty_question_fails_safely(client: TestClient):
    response = client.post(
        "/api/query",
        json={"question": "   ", "document_id": "demo-simple-001"},
    )
    assert response.status_code == 400
    assert "Query question cannot be empty" in response.json()["detail"]


def test_api_query_missing_document(client: TestClient):
    response = client.post(
        "/api/query",
        json={"question": "What is downstream of P-101?", "document_id": "nonexistent-doc"},
    )
    assert response.status_code == 404
    assert "Document graph not found" in response.json()["detail"]


def test_api_query_performs_no_graph_mutation(client: TestClient):
    """Guarantees that querying through the HTTP API performs no mutation on the registered graph."""
    graph = get_document_graph("demo-simple-001")
    assert graph is not None

    nodes_before = set(graph._nodes.keys())
    edges_before = [(e.source, e.target, e.relationship) for e in graph._edges]

    # Execute multiple queries via API
    client.post("/api/query", json={"question": "What is downstream of P-101?", "document_id": "demo-simple-001"})
    client.post("/api/query", json={"question": "What is upstream of V-102?", "document_id": "demo-simple-001"})
    client.post("/api/query", json={"question": "What is connected to P-101?", "document_id": "demo-simple-001"})

    nodes_after = set(graph._nodes.keys())
    edges_after = [(e.source, e.target, e.relationship) for e in graph._edges]

    assert nodes_before == nodes_after
    assert edges_before == edges_after

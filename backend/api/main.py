"""FastAPI web layer for HRIDAY."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.intelligence.graph.builder import build_graph
from backend.intelligence.graph.interfaces import GraphStore
from backend.orchestration.pipeline import QueryOrchestrator

app = FastAPI(title="HRIDAY", version="0.1.0", description="Sovereign industrial P&ID intelligence workbench")

# In-memory document graph registry for active session/demo execution
_GRAPH_REGISTRY: dict[str, GraphStore] = {}
_orchestrator = QueryOrchestrator()


def set_document_graph(document_id: str, graph: GraphStore) -> None:
    """Registers an in-memory GraphStore instance for an active document."""
    _GRAPH_REGISTRY[document_id] = graph


def get_document_graph(document_id: str) -> GraphStore | None:
    """Retrieves GraphStore for document_id, falling back to simple_pid fixture if requested."""
    if document_id in _GRAPH_REGISTRY:
        return _GRAPH_REGISTRY[document_id]

    # Default demo document fallback
    if document_id in ("demo-simple-001", "demo", "demo-pid"):
        fixture_path = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "simple_pid.json"
        if fixture_path.exists():
            data = json.loads(fixture_path.read_text(encoding="utf-8"))
            topology = {"nodes": data.get("entities", []), "edges": data.get("edges", [])}
            graph = build_graph(topology)
            _GRAPH_REGISTRY[document_id] = graph
            return graph

    return None


class QueryRequest(BaseModel):
    question: str
    document_id: str = "demo-simple-001"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "hriday-api"}


@app.post("/api/query")
def query_graph(request: QueryRequest) -> dict[str, Any]:
    """Routes natural language query through orchestration and query engine to graph store."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Query question cannot be empty")

    graph = get_document_graph(request.document_id)
    if graph is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document graph not found for document_id: '{request.document_id}'",
        )

    try:
        answer = _orchestrator.execute_query(
            question=request.question,
            graph=graph,
            document_id=request.document_id,
        )
        return answer.to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

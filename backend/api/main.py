"""FastAPI application entry point and thin integration boundary."""
from __future__ import annotations
from typing import Any, Callable
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.intelligence.graph.interfaces import GraphStore
from backend.orchestration.pipeline import QueryOrchestrator

app = FastAPI(title="HRIDAY", version="0.1.0", description="Sovereign industrial P&ID intelligence workbench")

# Thin delegation orchestrator (owned by M1 orchestration)
_orchestrator = QueryOrchestrator()

# Graph resolver callable hook: Allows caller / session runner to supply the active GraphStore.
# Defaults to None: no hardcoded fixtures, no second source of truth.
_graph_provider: Callable[[str], GraphStore | None] | None = None


def set_graph_provider(provider: Callable[[str], GraphStore | None] | None) -> None:
    """Configure the active graph resolver callable."""
    global _graph_provider
    _graph_provider = provider


class QueryRequest(BaseModel):
    question: str
    document_id: str = "demo-pid"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "hriday-api"}


@app.post("/api/query")
def query(request: QueryRequest) -> dict[str, Any]:
    """Thin integration route delegating queries through QueryOrchestrator."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Query question cannot be empty")

    if _graph_provider is None:
        raise HTTPException(
            status_code=503,
            detail="No graph provider configured for active documents",
        )

    graph = _graph_provider(request.document_id)
    if graph is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document graph not found for document_id: {request.document_id!r}",
        )

    try:
        answer = _orchestrator.execute_query(
            question=request.question,
            graph=graph,
            document_id=request.document_id,
        )
        if hasattr(answer, "to_dict"):
            return answer.to_dict()
        if isinstance(answer, dict):
            return answer
        return {"answer": str(answer)}
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

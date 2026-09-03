"""Read-only tool surface exposed to the agent."""
from __future__ import annotations


def downstream(graph, entity: str, depth: int | None = None):
    return graph.downstream(entity, depth)


def upstream(graph, entity: str, depth: int | None = None):
    return graph.upstream(entity, depth)

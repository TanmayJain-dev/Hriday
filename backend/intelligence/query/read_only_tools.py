"""Read-only graph tool surface available to the local agent."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.intelligence.graph.interfaces import GraphStore
    from backend.intelligence.graph.models import GraphNode

def downstream(graph: GraphStore, entity: str, depth: int | None = None) -> list[list[str]]:
    """Traverse downstream directed paths from the specified entity."""
    return graph.downstream(entity, depth)

def upstream(graph: GraphStore, entity: str, depth: int | None = None) -> list[list[str]]:
    """Traverse upstream directed paths leading to the specified entity."""
    return graph.upstream(entity, depth)

def neighbors(graph: GraphStore, entity: str, relationship: str | None = None) -> list[GraphNode]:
    """Retrieve immediate neighbors of the specified entity."""
    return graph.get_neighbors(entity, relationship)

def get_node(graph: GraphStore, entity: str) -> GraphNode | None:
    """Retrieve node details for the specified entity, or None if not found."""
    return graph.get_node(entity)

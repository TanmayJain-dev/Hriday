"""Read-only graph tool surface available to the local agent."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.intelligence.graph.interfaces import GraphStore
    from backend.intelligence.graph.models import GraphNode, GraphPath


def downstream(graph: GraphStore, entity: str, depth: int | None = None) -> list[list[str]]:
    """Traverse downstream directed paths from the specified entity."""
    return graph.downstream(entity, depth)


def upstream(graph: GraphStore, entity: str, depth: int | None = None) -> list[list[str]]:
    """Traverse upstream directed paths leading to the specified entity."""
    return graph.upstream(entity, depth)


def paths_between(
    graph: GraphStore,
    source: str,
    target: str,
    max_depth: int | None = None,
) -> list[list[str]]:
    """Find all directed simple paths between source and target entities."""
    return graph.paths_between(source, target, max_depth)


def neighbors(
    graph: GraphStore,
    entity: str,
    relationship: str | None = None,
) -> list[GraphNode]:
    """Retrieve immediate outgoing neighbors of the specified entity."""
    return graph.get_neighbors(entity, relationship)


def get_node(graph: GraphStore, entity: str) -> GraphNode | None:
    """Retrieve node details for the specified entity, or None if not found."""
    return graph.get_node(entity)


def downstream_detailed(
    graph: GraphStore,
    entity: str,
    depth: int | None = None,
) -> list[dict[str, Any]]:
    """Traverse downstream paths returning path confidence and provenance evidence IDs."""
    paths: list[GraphPath] = graph.downstream_paths(entity, depth)
    return [p.to_dict() for p in paths]


def upstream_detailed(
    graph: GraphStore,
    entity: str,
    depth: int | None = None,
) -> list[dict[str, Any]]:
    """Traverse upstream paths returning path confidence and provenance evidence IDs."""
    paths: list[GraphPath] = graph.upstream_paths(entity, depth)
    return [p.to_dict() for p in paths]


def paths_between_detailed(
    graph: GraphStore,
    source: str,
    target: str,
    max_depth: int | None = None,
) -> list[dict[str, Any]]:
    """Traverse directed paths between two entities with path confidence and provenance."""
    paths: list[GraphPath] = graph.paths_between_detailed(source, target, max_depth)
    return [p.to_dict() for p in paths]

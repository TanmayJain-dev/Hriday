"""Canonical read-only graph query tool surface.

Owned by Member 1 (Core Architecture & Graph Intelligence).
Provides strictly read-only, deterministic graph query operations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .interfaces import GraphStore
    from .models import GraphNode, GraphPath

__all__ = [
    "downstream",
    "upstream",
    "paths_between",
    "neighbors",
    "get_node",
    "downstream_detailed",
    "upstream_detailed",
    "paths_between_detailed",
]


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

"""Compatibility re-export of canonical read-only graph query tools for query layer.

This module preserves complete backward compatibility for query layer consumers.
The canonical implementations reside in `backend.intelligence.graph.read_only_tools`.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.intelligence.graph.interfaces import GraphStore
    from backend.intelligence.graph.models import GraphEdge, GraphNode

try:
    from backend.intelligence.graph.read_only_tools import (
        downstream,
        downstream_detailed,
        get_edge,
        get_node,
        neighbors,
        paths_between,
        paths_between_detailed,
        upstream,
        upstream_detailed,
    )
except ImportError:
    def downstream(graph: GraphStore, entity: str, depth: int | None = None) -> list[list[str]]:
        return graph.downstream(entity, depth)

    def upstream(graph: GraphStore, entity: str, depth: int | None = None) -> list[list[str]]:
        return graph.upstream(entity, depth)

    def paths_between(graph: GraphStore, source: str, target: str, max_depth: int | None = None) -> list[list[str]]:
        if hasattr(graph, "paths_between"):
            return graph.paths_between(source, target, max_depth)
        return []

    def neighbors(graph: GraphStore, entity: str, relationship: str | None = None) -> list[GraphNode]:
        return graph.get_neighbors(entity, relationship)

    def get_node(graph: GraphStore, entity: str) -> GraphNode | None:
        return graph.get_node(entity)

    def get_edge(graph: GraphStore, source: str, target: str, relationship: str | None = None) -> GraphEdge | None:
        if hasattr(graph, "get_edge"):
            return graph.get_edge(source, target, relationship)
        return None

    def downstream_detailed(graph: GraphStore, entity: str, depth: int | None = None) -> list[dict[str, Any]]:
        if hasattr(graph, "downstream_paths"):
            paths = graph.downstream_paths(entity, depth)
            return [p.to_dict() for p in paths]
        return []

    def upstream_detailed(graph: GraphStore, entity: str, depth: int | None = None) -> list[dict[str, Any]]:
        if hasattr(graph, "upstream_paths"):
            paths = graph.upstream_paths(entity, depth)
            return [p.to_dict() for p in paths]
        return []

    def paths_between_detailed(graph: GraphStore, source: str, target: str, max_depth: int | None = None) -> list[dict[str, Any]]:
        if hasattr(graph, "paths_between_detailed"):
            paths = graph.paths_between_detailed(source, target, max_depth)
            return [p.to_dict() for p in paths]
        return []

__all__ = [
    "downstream",
    "upstream",
    "paths_between",
    "neighbors",
    "get_node",
    "get_edge",
    "downstream_detailed",
    "upstream_detailed",
    "paths_between_detailed",
]

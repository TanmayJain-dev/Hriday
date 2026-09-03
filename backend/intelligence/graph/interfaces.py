"""Stable graph contract shared by topology, query, and orchestration layers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    attributes: dict[str, Any]
    confidence: float


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relationship: str
    attributes: dict[str, Any]
    confidence: float
    evidence_ids: tuple[str, ...] = ()


class GraphStore(Protocol):
    """Read-only consumer contract plus controlled mutation primitives."""

    def add_node(self, node: GraphNode) -> None: ...
    def add_edge(self, edge: GraphEdge) -> None: ...
    def get_node(self, node_id: str) -> GraphNode | None: ...
    def get_neighbors(self, node_id: str, relationship: str | None = None) -> list[GraphNode]: ...
    def downstream(self, node_id: str, max_depth: int | None = None) -> list[list[str]]: ...
    def upstream(self, node_id: str, max_depth: int | None = None) -> list[list[str]]: ...

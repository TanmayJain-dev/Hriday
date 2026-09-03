"""Dependency-free directed graph store for the MVP."""
from __future__ import annotations
from collections import deque
from .interfaces import GraphEdge, GraphNode


class NetworkXGraphStore:
    """In-memory graph with deterministic traversal semantics.

    Despite the class name, the MVP intentionally avoids requiring NetworkX;
    the GraphStore interface lets a real NetworkX or Neo4j implementation be
    introduced later without changing callers.
    """
    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        self._nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise ValueError("Both edge endpoints must exist before adding an edge")
        self._edges.append(edge)

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str, relationship: str | None = None) -> list[GraphNode]:
        seen: set[str] = set()
        result: list[GraphNode] = []
        for edge in self._edges:
            if edge.source != node_id:
                continue
            if relationship is not None and edge.relationship != relationship:
                continue
            if edge.target not in seen:
                seen.add(edge.target)
                result.append(self._nodes[edge.target])
        return result

    def _traverse(self, node_id: str, direction: str, max_depth: int | None) -> list[list[str]]:
        if node_id not in self._nodes:
            return []
        paths: list[list[str]] = []
        queue: deque[list[str]] = deque([[node_id]])
        while queue:
            path = queue.popleft()
            if max_depth is not None and len(path) - 1 >= max_depth:
                continue
            current = path[-1]
            for edge in self._edges:
                if direction == "downstream":
                    if edge.source != current:
                        continue
                    nxt = edge.target
                else:
                    if edge.target != current:
                        continue
                    nxt = edge.source
                if nxt in path:
                    continue
                next_path = [*path, nxt]
                paths.append(next_path)
                queue.append(next_path)
        return paths

    def downstream(self, node_id: str, max_depth: int | None = None) -> list[list[str]]:
        return self._traverse(node_id, "downstream", max_depth)

    def upstream(self, node_id: str, max_depth: int | None = None) -> list[list[str]]:
        return self._traverse(node_id, "upstream", max_depth)

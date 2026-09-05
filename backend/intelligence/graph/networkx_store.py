"""Dependency-free directed graph store for the MVP."""
from __future__ import annotations
from collections import deque
from typing import Any
from .models import GraphEdge, GraphNode, GraphPath, GraphResult


class NetworkXGraphStore:
    """In-memory directed graph store implementing the GraphStore protocol.

    Named NetworkXGraphStore for architectural compatibility with future NetworkX/Neo4j
    adapters, implemented without external dependencies for lightweight edge deployment.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        self._nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise ValueError(f"Both edge endpoints must exist: {edge.source} -> {edge.target}")
        self._edges.append(edge)

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def get_edge(self, source: str, target: str, relationship: str | None = None) -> GraphEdge | None:
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                if relationship is None or edge.relationship == relationship:
                    return edge
        return None

    def get_edges(
        self,
        source: str | None = None,
        target: str | None = None,
        relationship: str | None = None,
    ) -> list[GraphEdge]:
        result: list[GraphEdge] = []
        for edge in self._edges:
            if source is not None and edge.source != source:
                continue
            if target is not None and edge.target != target:
                continue
            if relationship is not None and edge.relationship != relationship:
                continue
            result.append(edge)
        return result

    def get_neighbors(self, node_id: str, relationship: str | None = None) -> list[GraphNode]:
        seen: set[str] = set()
        result: list[GraphNode] = []
        for edge in self._edges:
            if edge.source != node_id:
                continue
            if relationship is not None and edge.relationship != relationship:
                continue
            if edge.target not in seen and edge.target in self._nodes:
                seen.add(edge.target)
                result.append(self._nodes[edge.target])
        return result

    def all_nodes(self) -> list[GraphNode]:
        return list(self._nodes.values())

    def all_edges(self) -> list[GraphEdge]:
        return list(self._edges)

    def _traverse_detailed(
        self,
        node_id: str,
        direction: str,
        max_depth: int | None,
        target_id: str | None = None,
    ) -> list[GraphPath]:
        if node_id not in self._nodes:
            return []

        detailed_paths: list[GraphPath] = []
        # Queue contains tuple: (node_sequence, edge_sequence)
        queue: deque[tuple[list[str], list[GraphEdge]]] = deque([([node_id], [])])

        while queue:
            curr_nodes, curr_edges = queue.popleft()
            if max_depth is not None and len(curr_nodes) - 1 >= max_depth:
                continue

            current = curr_nodes[-1]
            for edge in self._edges:
                if direction == "downstream" and edge.source != current:
                    continue
                if direction == "upstream" and edge.target != current:
                    continue

                nxt = edge.target if direction == "downstream" else edge.source
                if nxt in curr_nodes:
                    # Prevent cycle traversal
                    continue

                next_nodes = [*curr_nodes, nxt]
                next_edges = [*curr_edges, edge]
                graph_path = GraphPath(nodes=tuple(next_nodes), edges=tuple(next_edges))

                if target_id is None or nxt == target_id:
                    detailed_paths.append(graph_path)

                if target_id is None or nxt != target_id:
                    queue.append((next_nodes, next_edges))

        return detailed_paths

    def downstream(self, node_id: str, max_depth: int | None = None) -> list[list[str]]:
        paths = self._traverse_detailed(node_id, "downstream", max_depth)
        return [list(p.nodes) for p in paths]

    def upstream(self, node_id: str, max_depth: int | None = None) -> list[list[str]]:
        paths = self._traverse_detailed(node_id, "upstream", max_depth)
        return [list(p.nodes) for p in paths]

    def paths_between(self, source: str, target: str, max_depth: int | None = None) -> list[list[str]]:
        paths = self._traverse_detailed(source, "downstream", max_depth, target_id=target)
        return [list(p.nodes) for p in paths]

    def downstream_paths(self, node_id: str, max_depth: int | None = None) -> list[GraphPath]:
        return self._traverse_detailed(node_id, "downstream", max_depth)

    def upstream_paths(self, node_id: str, max_depth: int | None = None) -> list[GraphPath]:
        return self._traverse_detailed(node_id, "upstream", max_depth)

    def paths_between_detailed(self, source: str, target: str, max_depth: int | None = None) -> list[GraphPath]:
        return self._traverse_detailed(source, "downstream", max_depth, target_id=target)

    def subgraph(self, node_ids: list[str]) -> NetworkXGraphStore:
        sub = NetworkXGraphStore()
        node_set = set(node_ids)
        for nid in node_ids:
            node = self.get_node(nid)
            if node:
                sub.add_node(node)
        for edge in self._edges:
            if edge.source in node_set and edge.target in node_set:
                sub.add_edge(edge)
        return sub

    def to_dict(self, document_id: str) -> dict[str, Any]:
        result = GraphResult(
            document_id=document_id,
            nodes=[n.to_dict() for n in self._nodes.values()],
            edges=[e.to_dict() for e in self._edges],
        )
        return result.to_dict()

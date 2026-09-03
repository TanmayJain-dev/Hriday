"""Build graph facts from topology results without inventing relationships."""
from __future__ import annotations

from .models import GraphEdge, GraphNode
from .networkx_store import NetworkXGraphStore


def build_graph(topology: dict) -> NetworkXGraphStore:
    store = NetworkXGraphStore()
    for node in topology.get("nodes", []):
        store.add_node(GraphNode(
            id=node["id"],
            type=node.get("type", "unknown"),
            attributes=node.get("attributes", {}),
            confidence=float(node.get("confidence", 1.0)),
        ))
    for edge in topology.get("edges", []):
        if edge.get("requires_verification", False):
            continue
        store.add_edge(GraphEdge(
            source=edge["source"],
            target=edge["target"],
            relationship=edge.get("relationship", "CONNECTED_TO"),
            attributes=edge.get("attributes", {}),
            confidence=float(edge.get("confidence", 1.0)),
            evidence_ids=tuple(edge.get("evidence_ids", [])),
        ))
    return store

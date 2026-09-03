"""Build graph facts from topology results without inventing relationships."""
from .models import GraphEdge, GraphNode
from .networkx_store import NetworkXGraphStore

def build_graph(topology: dict) -> NetworkXGraphStore:
    store = NetworkXGraphStore()
    for node in topology.get("nodes", []):
        store.add_node(GraphNode(node["id"], node.get("type", "unknown"), node.get("attributes", {}), float(node.get("confidence", 1.0))))
    for edge in topology.get("edges", []):
        if edge.get("requires_verification", False):
            continue
        store.add_edge(GraphEdge(edge["source"], edge["target"], edge.get("relationship", "CONNECTED_TO"), edge.get("attributes", {}), float(edge.get("confidence", 1.0)), tuple(edge.get("evidence_ids", []))))
    return store

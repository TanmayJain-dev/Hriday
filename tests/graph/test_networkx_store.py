from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore


def make_graph() -> NetworkXGraphStore:
    graph = NetworkXGraphStore()
    for node_id, node_type in [("V-101", "vessel"), ("P-101", "pump"), ("E-101", "exchanger"), ("V-102", "vessel")]:
        graph.add_node(GraphNode(node_id, node_type))
    graph.add_edge(GraphEdge("V-101", "P-101", "FLOWS_TO"))
    graph.add_edge(GraphEdge("P-101", "E-101", "FLOWS_TO"))
    graph.add_edge(GraphEdge("E-101", "V-102", "FLOWS_TO"))
    return graph


def test_downstream_paths():
    graph = make_graph()
    assert ["P-101", "E-101"] in graph.downstream("P-101")
    assert ["P-101", "E-101", "V-102"] in graph.downstream("P-101")


def test_missing_node_returns_empty_paths():
    assert make_graph().downstream("X-999") == []

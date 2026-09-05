from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore
from backend.intelligence.query.models import QueryIntent
from backend.intelligence.query.planner import execute_intent


def test_downstream_intent():
    graph = NetworkXGraphStore()
    graph.add_node(GraphNode("P-101", "pump"))
    graph.add_node(GraphNode("E-101", "exchanger"))
    graph.add_edge(GraphEdge("P-101", "E-101", "FLOWS_TO", confidence=1.0))
    assert ["P-101", "E-101"] in execute_intent(graph, QueryIntent("DOWNSTREAM", "P-101"))

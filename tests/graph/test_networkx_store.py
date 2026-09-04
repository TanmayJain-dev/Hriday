from backend.intelligence.graph.interfaces import GraphEdge, GraphNode
from backend.intelligence.graph.networkx_store import NetworkXGraphStore


def make_graph() -> NetworkXGraphStore:
    graph = NetworkXGraphStore()
    for node_id, node_type in [("V-101", "vessel"), ("P-101", "pump"), ("E-101", "exchanger"), ("V-102", "vessel")]:
        graph.add_node(GraphNode(node_id, node_type))
    graph.add_edge(GraphEdge("V-101", "P-101", "FLOWS_TO", confidence=0.98, evidence_ids=("ev-1",)))
    graph.add_edge(GraphEdge("P-101", "E-101", "FLOWS_TO", confidence=0.92, evidence_ids=("ev-2",)))
    graph.add_edge(GraphEdge("E-101", "V-102", "FLOWS_TO", confidence=0.95, evidence_ids=("ev-3",)))
    return graph


def test_downstream_paths():
    graph = make_graph()
    assert ["P-101", "E-101"] in graph.downstream("P-101")
    assert ["P-101", "E-101", "V-102"] in graph.downstream("P-101")


def test_upstream_paths():
    graph = make_graph()
    assert ["E-101", "P-101"] in graph.upstream("E-101")
    assert ["E-101", "P-101", "V-101"] in graph.upstream("E-101")


def test_paths_between():
    graph = make_graph()
    paths = graph.paths_between("V-101", "V-102")
    assert len(paths) == 1
    assert paths[0] == ["V-101", "P-101", "E-101", "V-102"]

    # Non-existent target
    assert graph.paths_between("V-101", "NON-EXISTENT") == []


def test_detailed_paths_propagation():
    graph = make_graph()
    detailed = graph.paths_between_detailed("V-101", "V-102")
    assert len(detailed) == 1
    path = detailed[0]
    assert path.nodes == ("V-101", "P-101", "E-101", "V-102")
    # Path confidence should be min(0.98, 0.92, 0.95) == 0.92
    assert path.confidence == 0.92
    assert set(path.evidence_ids) == {"ev-1", "ev-2", "ev-3"}


def test_cycle_prevention():
    graph = NetworkXGraphStore()
    graph.add_node(GraphNode("N-1", "node"))
    graph.add_node(GraphNode("N-2", "node"))
    graph.add_node(GraphNode("N-3", "node"))
    # Introduce cycle: N-1 -> N-2 -> N-3 -> N-1
    graph.add_edge(GraphEdge("N-1", "N-2"))
    graph.add_edge(GraphEdge("N-2", "N-3"))
    graph.add_edge(GraphEdge("N-3", "N-1"))

    # Downstream should terminate without infinite loop
    paths = graph.downstream("N-1")
    assert ["N-1", "N-2"] in paths
    assert ["N-1", "N-2", "N-3"] in paths
    # It should not contain duplicate node sequences beyond simple path
    for p in paths:
        assert len(p) == len(set(p))


def test_max_depth_limiting():
    graph = make_graph()
    # Depth 1: should only return immediate neighbors
    d1 = graph.downstream("V-101", max_depth=1)
    assert d1 == [["V-101", "P-101"]]

    # Depth 2: returns up to 2 hops
    d2 = graph.downstream("V-101", max_depth=2)
    assert ["V-101", "P-101"] in d2
    assert ["V-101", "P-101", "E-101"] in d2
    assert ["V-101", "P-101", "E-101", "V-102"] not in d2


def test_subgraph_extraction():
    graph = make_graph()
    sub = graph.subgraph(["P-101", "E-101"])
    assert sub.get_node("P-101") is not None
    assert sub.get_node("E-101") is not None
    assert sub.get_node("V-101") is None
    edges = sub.all_edges()
    assert len(edges) == 1
    assert edges[0].source == "P-101"
    assert edges[0].target == "E-101"


def test_missing_node_returns_empty_paths():
    assert make_graph().downstream("X-999") == []
    assert make_graph().upstream("X-999") == []


def test_edge_query_helpers():
    graph = make_graph()
    e = graph.get_edge("P-101", "E-101")
    assert e is not None
    assert e.source == "P-101"
    assert e.target == "E-101"

    edges = graph.get_edges(source="P-101")
    assert len(edges) == 1
    assert edges[0].target == "E-101"


def test_to_dict_conformance():
    graph = make_graph()
    d = graph.to_dict("demo-pid-01")
    assert d["document_id"] == "demo-pid-01"
    assert len(d["nodes"]) == 4
    assert len(d["edges"]) == 3

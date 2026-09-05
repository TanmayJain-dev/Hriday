"""Build graph facts from topology results without inventing relationships."""
from __future__ import annotations
from typing import Any
from .models import GraphEdge, GraphNode, GraphResult
from .networkx_store import NetworkXGraphStore

DEFAULT_CONFIDENCE_THRESHOLD = 0.70


def build_graph_with_uncertainties(
    topology: dict[str, Any],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> tuple[NetworkXGraphStore, list[dict[str, Any]]]:
    """Build a GraphStore from a TopologyResult, isolating unverified/uncertain claims.

    Non-negotiable rule: Do not create a graph edge without an evidence/rule path supporting it.
    Uncertain edges (confidence < threshold, requires_verification=True, or ambiguous) are routed
    to the uncertainties list for human review rather than asserted as graph facts.
    """
    store = NetworkXGraphStore()
    uncertainties: list[dict[str, Any]] = []

    # 1. Ingest existing uncertainties from topology
    for unc in topology.get("uncertainties", []):
        uncertainties.append(dict(unc))

    # Support candidate_edge / candidate_edges from fixtures
    if "candidate_edge" in topology:
        uncertainties.append(dict(topology["candidate_edge"]))
    for cand in topology.get("candidate_edges", []):
        uncertainties.append(dict(cand))

    # 2. Extract nodes (support both 'nodes' and 'entities' schema variants)
    raw_nodes = topology.get("nodes") or topology.get("entities") or []
    for node in raw_nodes:
        raw_conf = node.get("confidence")
        graph_node = GraphNode(
            id=str(node["id"]),
            type=str(node.get("type", "unknown")),
            attributes=dict(node.get("attributes", {})),
            confidence=float(raw_conf) if raw_conf is not None else None,
            evidence_ids=tuple(node.get("evidence_ids", ())),
        )
        store.add_node(graph_node)

    # 3. Extract edges, gating on verification flags, endpoint existence, and confidence
    raw_edges = topology.get("edges", [])
    seen_edges: set[tuple[str, str, str]] = set()
    for edge in raw_edges:
        raw_conf = edge.get("confidence")
        requires_verification = bool(edge.get("requires_verification", False))
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        relationship = str(edge.get("relationship", "CONNECTED_TO"))
        edge_key = (source, target, relationship)
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        # Check endpoints exist
        if not store.get_node(source) or not store.get_node(target):
            conf = float(raw_conf) if raw_conf is not None else 0.0
            uncertainties.append({
                "source": source,
                "target": target,
                "relationship": relationship,
                "confidence": conf,
                "reason": "missing_endpoint_node",
                "requires_verification": True,
                "evidence_ids": list(edge.get("evidence_ids", [])),
                "attributes": dict(edge.get("attributes", {})),
            })
            continue

        # Missing extraction/topology confidence cannot silently become 1.0 certainty
        if raw_conf is None:
            uncertainties.append({
                "source": source,
                "target": target,
                "relationship": relationship,
                "confidence": 0.0,
                "reason": "missing_confidence",
                "requires_verification": True,
                "evidence_ids": list(edge.get("evidence_ids", [])),
            })
            continue

        conf = float(raw_conf)

        # Check confidence gate and verification flag
        if requires_verification or conf < confidence_threshold:
            uncertainties.append({
                "source": source,
                "target": target,
                "relationship": relationship,
                "confidence": conf,
                "reason": edge.get("reason", "low_confidence" if conf < confidence_threshold else "verification_required"),
                "requires_verification": True,
                "evidence_ids": list(edge.get("evidence_ids", [])),
                "attributes": dict(edge.get("attributes", {})),
            })
            continue

        # Provenance invariant: a confirmed edge must have evidence/rule provenance
        raw_evidence = edge.get("evidence_ids")
        if not raw_evidence:
            uncertainties.append({
                "source": source,
                "target": target,
                "relationship": relationship,
                "confidence": conf,
                "reason": "missing_provenance",
                "requires_verification": True,
                "evidence_ids": [],
                "attributes": dict(edge.get("attributes", {})),
            })
            continue

        # Confirmed fact: persist edge
        store.add_edge(GraphEdge(
            source=source,
            target=target,
            relationship=relationship,
            confidence=conf,
            attributes=dict(edge.get("attributes", {})),
            evidence_ids=tuple(raw_evidence),
            requires_verification=requires_verification,
            reason=edge.get("reason"),
        ))

    return store, uncertainties


def build_graph(
    topology: dict[str, Any],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> NetworkXGraphStore:
    """Convenience wrapper returning the populated GraphStore."""
    store, _ = build_graph_with_uncertainties(topology, confidence_threshold)
    return store


def build_graph_result(
    topology: dict[str, Any],
    document_id: str | None = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> tuple[GraphResult, list[dict[str, Any]]]:
    """Build canonical GraphResult conforming to contracts/graph.schema.json."""
    store, uncertainties = build_graph_with_uncertainties(topology, confidence_threshold)
    doc_id = document_id or str(topology.get("document_id", "pid-unknown"))
    graph_dict = store.to_dict(doc_id)
    return GraphResult.from_dict(graph_dict), uncertainties

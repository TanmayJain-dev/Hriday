"""Graph-level validation hooks for topology and fact integrity."""
from __future__ import annotations
from typing import TYPE_CHECKING
from .models import GraphEdge, GraphNode

if TYPE_CHECKING:
    from .interfaces import GraphStore


def validate_node(node: GraphNode) -> list[str]:
    """Validate graph node schema and boundaries."""
    errors: list[str] = []
    if not node.id or not str(node.id).strip():
        errors.append("empty_node_id")
    if not node.type or not str(node.type).strip():
        errors.append("empty_node_type")
    if not 0.0 <= node.confidence <= 1.0:
        errors.append("confidence_out_of_range")
    return errors


def validate_edge(edge: GraphEdge, require_provenance: bool = False) -> list[str]:
    """Validate graph edge schema, endpoints, and confidence bounds."""
    errors: list[str] = []
    if not edge.source or not edge.target:
        errors.append("missing_endpoint")
    elif edge.source == edge.target:
        errors.append("self_referential_edge")
    if not 0.0 <= edge.confidence <= 1.0:
        errors.append("confidence_out_of_range")
    if require_provenance and not edge.evidence_ids:
        errors.append("missing_provenance")
    return errors


def validate_graph(graph: GraphStore) -> list[str]:
    """Validate overall graph consistency (endpoint existence, integrity)."""
    errors: list[str] = []
    for edge in graph.all_edges():
        if graph.get_node(edge.source) is None:
            errors.append(f"edge_source_missing_from_nodes:{edge.source}")
        if graph.get_node(edge.target) is None:
            errors.append(f"edge_target_missing_from_nodes:{edge.target}")
        edge_errors = validate_edge(edge)
        errors.extend(f"{edge.source}->{edge.target}:{e}" for e in edge_errors)
    for node in graph.all_nodes():
        node_errors = validate_node(node)
        errors.extend(f"{node.id}:{e}" for e in node_errors)
    return errors

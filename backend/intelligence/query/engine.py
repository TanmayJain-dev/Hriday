"""Deterministic query engine orchestrator for Member 5."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .explainer import FactGroundedAnswerExplainer
from .intent_resolution import RuleBasedIntentResolver
from .interfaces import AnswerExplainer, IntentResolver
from .models import Answer, GraphResult
from .planner import execute_intent

if TYPE_CHECKING:
    from backend.intelligence.graph.interfaces import GraphStore


class QueryEngine:
    """Orchestrates deterministic question answering over the P&ID engineering graph."""

    def __init__(
        self,
        intent_resolver: IntentResolver | None = None,
        explainer: AnswerExplainer | None = None,
    ) -> None:
        self.intent_resolver: IntentResolver = intent_resolver or RuleBasedIntentResolver()
        self.explainer: AnswerExplainer = explainer or FactGroundedAnswerExplainer()

    def query(
        self,
        question: str,
        graph: GraphStore,
        document_id: str = "demo-pid",
    ) -> Answer:
        """Executes a natural language query against the read-only graph store.

        Pipeline:
        1. Resolves query intent and normalizes entity (or entities) from question.
        2. Retrieves entity from graph (checking existence; preserving uncertainty if missing).
        3. Executes canonical read-only traversal (consuming GraphPath where available).
        4. Packages graph facts into GraphResult matching contracts/graph.schema.json.
        5. Synthesizes fact-grounded explanation.
        6. Preserves canonical weakest-link confidence and evidence provenance.
        7. Evaluates verification requirement against deterministic threshold (0.90).
        8. Assembles Answer matching contracts/answer.schema.json.
        """
        # Step 1: Intent & Entity Resolution
        intent = self.intent_resolver.resolve(question)

        # Step 2 & 3: Read-Only Graph Traversal consuming canonical APIs
        canonical_paths: list[Any] = []
        raw_paths: list[list[str]] = []
        involved_node_ids: set[str] = set()

        if intent.intent == "PATHS_BETWEEN":
            src_entity = intent.entity
            tgt_entity = intent.target_entity
            if src_entity:
                involved_node_ids.add(src_entity)
            if tgt_entity:
                involved_node_ids.add(tgt_entity)

            src_node = graph.get_node(src_entity) if src_entity else None
            tgt_node = graph.get_node(tgt_entity) if tgt_entity else None

            if src_node and tgt_node and src_entity and tgt_entity:
                if hasattr(graph, "paths_between_detailed"):
                    canonical_paths = graph.paths_between_detailed(src_entity, tgt_entity, intent.depth)
                    raw_paths = [list(p.nodes) for p in canonical_paths]
                elif hasattr(graph, "paths_between"):
                    raw_paths = graph.paths_between(src_entity, tgt_entity, intent.depth)

        elif intent.intent == "DOWNSTREAM":
            if intent.entity:
                involved_node_ids.add(intent.entity)
            node = graph.get_node(intent.entity) if intent.entity else None
            if node and intent.entity:
                if hasattr(graph, "downstream_paths"):
                    canonical_paths = graph.downstream_paths(intent.entity, intent.depth)
                    raw_paths = [list(p.nodes) for p in canonical_paths]
                else:
                    raw_paths = execute_intent(graph, intent)

        elif intent.intent == "UPSTREAM":
            if intent.entity:
                involved_node_ids.add(intent.entity)
            node = graph.get_node(intent.entity) if intent.entity else None
            if node and intent.entity:
                if hasattr(graph, "upstream_paths"):
                    canonical_paths = graph.upstream_paths(intent.entity, intent.depth)
                    raw_paths = [list(p.nodes) for p in canonical_paths]
                else:
                    raw_paths = execute_intent(graph, intent)

        elif intent.intent == "NEIGHBORS":
            if intent.entity:
                involved_node_ids.add(intent.entity)
            node = graph.get_node(intent.entity) if intent.entity else None
            if node and intent.entity:
                raw_paths = execute_intent(graph, intent)

        # Collect all involved nodes from discovered paths
        for path in raw_paths:
            involved_node_ids.update(path)

        # Structure nodes_list with preserved node confidence
        nodes_list: list[dict[str, Any]] = []
        node_confs: list[float] = []
        for nid in sorted(involved_node_ids):
            n = graph.get_node(nid)
            if n is not None:
                n_conf = getattr(n, "confidence", None)
                conf_val = float(n_conf) if n_conf is not None else 0.0
                node_entry: dict[str, Any] = {
                    "id": n.id,
                    "type": n.type,
                    "attributes": n.attributes,
                    "confidence": conf_val,
                }
                if getattr(n, "evidence_ids", None):
                    node_entry["evidence_ids"] = list(n.evidence_ids)
                nodes_list.append(node_entry)
                node_confs.append(conf_val)
            else:
                nodes_list.append({
                    "id": nid,
                    "type": "unknown",
                    "attributes": {},
                    "confidence": 0.0,
                })
                node_confs.append(0.0)

        # Structure edges_list, preserving canonical GraphEdge and GraphPath data
        edges_list: list[dict[str, Any]] = []
        seen_edges: set[tuple[str, str, str]] = set()
        edge_confs: list[float] = []
        evidence_ids_collected: list[str] = []

        if canonical_paths:
            # Consume canonical GraphPath / GraphEdge objects directly
            for p in canonical_paths:
                if hasattr(p, "confidence") and p.confidence is not None:
                    edge_confs.append(float(p.confidence))
                if hasattr(p, "evidence_ids") and p.evidence_ids:
                    for eid in p.evidence_ids:
                        if eid not in evidence_ids_collected:
                            evidence_ids_collected.append(eid)
                for edge in getattr(p, "edges", ()):
                    edge_key = (edge.source, edge.target, edge.relationship)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edge_dict: dict[str, Any] = {
                            "source": edge.source,
                            "target": edge.target,
                            "relationship": edge.relationship,
                            "confidence": float(edge.confidence),
                        }
                        if getattr(edge, "evidence_ids", None):
                            edge_dict["evidence_ids"] = list(edge.evidence_ids)
                        edges_list.append(edge_dict)
                        edge_confs.append(float(edge.confidence))
        else:
            # Fallback path traversal extracting edges and edge confidence safely
            get_edge_fn = getattr(graph, "get_edge", None)
            has_get_edge = callable(get_edge_fn)

            for path in raw_paths:
                for i in range(len(path) - 1):
                    if intent.intent == "UPSTREAM":
                        src, tgt = path[i + 1], path[i]
                    else:
                        src, tgt = path[i], path[i + 1]

                    default_rel = (
                        "FLOWS_TO"
                        if intent.intent in ("DOWNSTREAM", "UPSTREAM", "PATHS_BETWEEN")
                        else "CONNECTED_TO"
                    )
                    edge_key = (src, tgt, default_rel)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edge_entry: dict[str, Any] = {
                            "source": src,
                            "target": tgt,
                            "relationship": default_rel,
                        }

                        if has_get_edge:
                            edge_obj = get_edge_fn(src, tgt)
                            if edge_obj is not None:
                                if hasattr(edge_obj, "relationship"):
                                    edge_entry["relationship"] = edge_obj.relationship
                                if hasattr(edge_obj, "confidence") and edge_obj.confidence is not None:
                                    edge_conf = float(edge_obj.confidence)
                                    edge_entry["confidence"] = edge_conf
                                    edge_confs.append(edge_conf)
                                if hasattr(edge_obj, "evidence_ids") and edge_obj.evidence_ids:
                                    for eid in edge_obj.evidence_ids:
                                        if eid not in evidence_ids_collected:
                                            evidence_ids_collected.append(eid)
                                    edge_entry["evidence_ids"] = list(edge_obj.evidence_ids)

                        edges_list.append(edge_entry)

        graph_result = GraphResult(
            document_id=document_id,
            nodes=nodes_list,
            edges=edges_list,
        )

        # Step 5: Fact-Grounded Explanation
        text_answer = self.explainer.explain(question, raw_paths, evidence=None)

        # Step 6: Confidence calculation (conservative weakest link across facts)
        all_confs = node_confs + edge_confs
        confidence = min(all_confs) if all_confs else 0.0

        # Step 7: Verification determination (threshold: 0.90)
        verification = (
            {"status": "required", "reason": "low_confidence"}
            if confidence < 0.9
            else {"status": "not_required"}
        )

        # Step 8: Return Answer
        return Answer(
            answer=text_answer,
            confidence=confidence,
            graph_result=graph_result.to_dict(),
            evidence=list(evidence_ids_collected),
            verification=verification,
        )

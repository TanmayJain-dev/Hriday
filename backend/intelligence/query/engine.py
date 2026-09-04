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
        1. Resolves query intent and normalizes entity from question.
        2. Retrieves entity from graph (checking existence).
        3. Executes read-only traversal on graph (never mutating graph facts).
        4. Packages graph facts into GraphResult matching contracts/graph.schema.json.
        5. Synthesizes fact-grounded explanation.
        6. Calculates confidence from the weakest returned fact (min).
        7. Evaluates verification requirement.
        8. Assembles Answer matching contracts/answer.schema.json.
        """
        # Step 1: Intent & Entity Resolution
        intent = self.intent_resolver.resolve(question)

        # Step 2 & 3: Retrieve entity & Read-Only Graph Traversal
        node = graph.get_node(intent.entity) if intent.entity else None
        if not node:
            raw_paths: list[list[str]] = []
        else:
            raw_paths = execute_intent(graph, intent)

        # Step 4: Structure GraphResult (contracts/graph.schema.json)
        involved_node_ids: set[str] = set()
        if intent.entity:
            involved_node_ids.add(intent.entity)
        for path in raw_paths:
            involved_node_ids.update(path)

        nodes_list: list[dict[str, Any]] = []
        node_confs: list[float] = []
        for nid in sorted(involved_node_ids):
            n = graph.get_node(nid)
            if n is not None:
                n_conf = getattr(n, "confidence", None)
                conf_val = float(n_conf) if n_conf is not None else 0.0
                nodes_list.append({
                    "id": n.id,
                    "type": n.type,
                    "attributes": n.attributes,
                    "confidence": conf_val,
                })
                node_confs.append(conf_val)
            else:
                nodes_list.append({
                    "id": nid,
                    "type": "unknown",
                    "attributes": {},
                    "confidence": 0.0,
                })
                node_confs.append(0.0)

        # Collect directed edges traversed in paths
        edges_list: list[dict[str, Any]] = []
        seen_edges: set[tuple[str, str]] = set()
        edge_confs: list[float] = []
        get_edge_fn = getattr(graph, "get_edge", None)
        has_get_edge = callable(get_edge_fn)

        for path in raw_paths:
            for i in range(len(path) - 1):
                # Semantically correct relationship direction (Audit 8):
                # Upstream traversal moves backwards from entity to upstream origins.
                # The physical directed graph edge flows from path[i+1] to path[i].
                if intent.intent == "UPSTREAM":
                    src, tgt = path[i + 1], path[i]
                else:
                    src, tgt = path[i], path[i + 1]

                edge_key = (src, tgt)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    default_rel = "FLOWS_TO" if intent.intent in ("DOWNSTREAM", "UPSTREAM") else "CONNECTED_TO"
                    edge_entry: dict[str, Any] = {
                        "source": src,
                        "target": tgt,
                        "relationship": default_rel,
                    }

                    # Safely extract edge facts only if exposed through public method
                    if has_get_edge:
                        edge_obj = get_edge_fn(src, tgt)
                        if edge_obj is not None:
                            if hasattr(edge_obj, "relationship"):
                                edge_entry["relationship"] = edge_obj.relationship
                            if hasattr(edge_obj, "confidence") and edge_obj.confidence is not None:
                                edge_conf = float(edge_obj.confidence)
                                edge_entry["confidence"] = edge_conf
                                edge_confs.append(edge_conf)

                    edges_list.append(edge_entry)

        graph_result = GraphResult(
            document_id=document_id,
            nodes=nodes_list,
            edges=edges_list,
        )

        # Step 5: Fact-Grounded Explanation
        text_answer = self.explainer.explain(question, raw_paths, evidence=None)

        # Step 6: Confidence calculation (weakest returned fact)
        # Combines all legitimately available facts (nodes and any exposed edges)
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
            evidence=[],
            verification=verification,
        )

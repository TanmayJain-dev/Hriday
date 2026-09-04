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
        2. Executes read-only traversal on graph (never mutating graph facts).
        3. Packages graph facts into GraphResult matching contracts/graph.schema.json.
        4. Synthesizes fact-grounded explanation.
        5. Assembles Answer matching contracts/answer.schema.json.
        """
        # Step 1: Intent & Entity Resolution
        intent = self.intent_resolver.resolve(question)

        # Step 2: Read-Only Graph Operation
        node = graph.get_node(intent.entity) if intent.entity else None
        if not node:
            raw_paths: list[list[str]] = []
        else:
            raw_paths = execute_intent(graph, intent)

        # Step 3: Structure GraphResult (contracts/graph.schema.json)
        involved_node_ids: set[str] = set()
        if intent.entity:
            involved_node_ids.add(intent.entity)
        for path in raw_paths:
            involved_node_ids.update(path)

        nodes_list: list[dict[str, Any]] = []
        for nid in sorted(involved_node_ids):
            n = graph.get_node(nid)
            if n is not None:
                nodes_list.append({
                    "id": n.id,
                    "type": n.type,
                    "attributes": n.attributes,
                    "confidence": n.confidence,
                })
            else:
                nodes_list.append({
                    "id": nid,
                    "type": "unknown",
                    "attributes": {},
                    "confidence": 1.0,
                })

        # Collect directed edges traversed in paths
        edges_list: list[dict[str, Any]] = []
        seen_edges: set[tuple[str, str]] = set()
        for path in raw_paths:
            for i in range(len(path) - 1):
                src, tgt = path[i], path[i + 1]
                edge_key = (src, tgt)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges_list.append({
                        "source": src,
                        "target": tgt,
                        "relationship": "FLOWS_TO" if intent.intent in ("DOWNSTREAM", "UPSTREAM") else "CONNECTED_TO",
                        "confidence": 1.0,
                    })

        graph_result = GraphResult(
            document_id=document_id,
            nodes=nodes_list,
            edges=edges_list,
        )

        # Step 4: Fact-Grounded Explanation
        text_answer = self.explainer.explain(question, raw_paths, evidence=None)

        # Step 5: Assemble Final Answer (contracts/answer.schema.json)
        confidence = 1.0
        if nodes_list:
            node_confs = [n["confidence"] for n in nodes_list if "confidence" in n]
            if node_confs:
                confidence = round(sum(node_confs) / len(node_confs), 2)

        return Answer(
            answer=text_answer,
            confidence=confidence,
            graph_result=graph_result.to_dict(),
            evidence=[],  # Evidence not fabricated; left empty if not present in graph result
            verification={"status": "not_required"},
        )

"""Fact-grounded answer explanation strictly derived from graph facts."""
from __future__ import annotations
from typing import Any
from .entity_resolution import extract_and_normalize_entity
from .intent_resolution import detect_intent


class FactGroundedAnswerExplainer:
    """Generates explanations strictly grounded in retrieved graph facts.
    
    Adheres strictly to the truth hierarchy: never fabricates connections,
    never conceals absence of data, and references only retrieved facts.
    """

    def explain(self, question: str, graph_result: Any, evidence: Any = None) -> str:
        entity = extract_and_normalize_entity(question) or "Target entity"
        intent = detect_intent(question) or "QUERY"

        # Handle list of paths (standard traversal result from graph tools)
        if isinstance(graph_result, list):
            paths: list[list[str]] = [p for p in graph_result if isinstance(p, list)]
            if not paths:
                if intent == "DOWNSTREAM":
                    return f"No downstream equipment found connected to {entity}."
                if intent == "UPSTREAM":
                    return f"No upstream equipment found connected to {entity}."
                if intent == "NEIGHBORS":
                    return f"No connected equipment found for {entity}."
                if intent == "PATHS_BETWEEN":
                    from .entity_resolution import extract_source_and_target
                    src, tgt = extract_source_and_target(question)
                    return f"No directed path found connecting {src or entity} to {tgt or 'target'}."
                return f"No graph facts found for {entity}."

            # Collect reachable target equipment (excluding starting entity)
            targets: list[str] = []
            seen: set[str] = set()
            for path in paths:
                for node_id in path:
                    if node_id != entity and node_id not in seen:
                        seen.add(node_id)
                        targets.append(node_id)

            formatted_paths = [" -> ".join(p) for p in paths]
            targets_str = ", ".join(targets) if targets else "None"

            if intent == "PATHS_BETWEEN":
                from .entity_resolution import extract_source_and_target
                src, tgt = extract_source_and_target(question)
                return f"Path from {src or entity} to {tgt or 'target'}: {', '.join(formatted_paths)}."
            if intent == "DOWNSTREAM":
                return f"Downstream of {entity}: {targets_str}. Paths: {', '.join(formatted_paths)}."
            if intent == "UPSTREAM":
                return f"Upstream of {entity}: {targets_str}. Paths: {', '.join(formatted_paths)}."
            if intent == "NEIGHBORS":
                return f"Directly connected to {entity}: {targets_str}."


            return f"Found {len(paths)} path(s) involving {entity}: {', '.join(formatted_paths)}."

        # Handle dictionary / GraphResult payload
        if isinstance(graph_result, dict):
            nodes = graph_result.get("nodes", [])
            node_ids = [n.get("id") for n in nodes if isinstance(n, dict) and n.get("id") != entity]
            if not node_ids:
                return f"No related equipment found for {entity}."
            return f"Retrieved {len(node_ids)} equipment item(s) related to {entity}: {', '.join(node_ids)}."

        return f"Retrieved graph facts for {entity}: {graph_result!s}"

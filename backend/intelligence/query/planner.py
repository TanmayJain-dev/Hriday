"""Deterministic query semantics used by the agent/tool layer."""
from .models import QueryIntent

SUPPORTED_INTENTS = {"DOWNSTREAM", "UPSTREAM", "NEIGHBORS"}

def execute_intent(graph, intent: QueryIntent):
    if intent.intent not in SUPPORTED_INTENTS:
        raise ValueError(f"Unsupported query intent: {intent.intent}")
    if not intent.entity:
        raise ValueError("Query intent requires an entity")
    if intent.intent == "DOWNSTREAM":
        return graph.downstream(intent.entity, intent.depth)
    if intent.intent == "UPSTREAM":
        return graph.upstream(intent.entity, intent.depth)
    return [[intent.entity, n.id] for n in graph.get_neighbors(intent.entity)]

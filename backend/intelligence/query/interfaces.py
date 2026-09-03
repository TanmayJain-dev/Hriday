"""Provider boundaries for future local LLM integrations."""
from __future__ import annotations
from typing import Protocol

from .models import QueryIntent


class IntentResolver(Protocol):
    def resolve(self, question: str) -> QueryIntent: ...


class AnswerExplainer(Protocol):
    def explain(self, question: str, graph_result: object, evidence: object) -> str: ...

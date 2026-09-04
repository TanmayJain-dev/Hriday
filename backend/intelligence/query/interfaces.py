from __future__ import annotations
from typing import Any, Protocol
from .models import QueryIntent

class IntentResolver(Protocol):
    def resolve(self, question: str) -> QueryIntent: ...

class AnswerExplainer(Protocol):
    def explain(self, question: str, graph_result: object, evidence: object = None) -> str: ...

class ModelAdapter(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> str: ...

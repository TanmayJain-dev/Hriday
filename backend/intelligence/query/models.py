"""Query intent models independent of any LLM SDK."""
from dataclasses import dataclass

@dataclass(frozen=True)
class QueryIntent:
    intent: str
    entity: str | None = None
    depth: int | None = None

"""Deterministic intent resolution for P&ID engineering queries."""
from __future__ import annotations
import re
from .entity_resolution import extract_and_normalize_entity
from .models import QueryIntent

# Deterministic pattern triggers for supported graph query intents
_DOWNSTREAM_PATTERNS = [
    re.compile(r"\bdownstream\b", re.IGNORECASE),
    re.compile(r"\bcomes?\s+after\b", re.IGNORECASE),
    re.compile(r"\bflows?\s+(?:to|into)\b", re.IGNORECASE),
    re.compile(r"\bfeeds?\b", re.IGNORECASE),
    re.compile(r"\bleaves?\b", re.IGNORECASE),
    re.compile(r"\boutflow\b", re.IGNORECASE),
]

_UPSTREAM_PATTERNS = [
    re.compile(r"\bupstream\b", re.IGNORECASE),
    re.compile(r"\bcomes?\s+(?:from|before)\b", re.IGNORECASE),
    re.compile(r"\bbefore\b", re.IGNORECASE),
    re.compile(r"\bfed\s+by\b", re.IGNORECASE),
    re.compile(r"\bsource\s+of\b", re.IGNORECASE),
    re.compile(r"\bflows?\s+from\b", re.IGNORECASE),
    re.compile(r"\binflow\b", re.IGNORECASE),
]

_NEIGHBORS_PATTERNS = [
    re.compile(r"\bconnected\s+(?:to|with)\b", re.IGNORECASE),
    re.compile(r"\bneighbors?\s*(?:of)?\b", re.IGNORECASE),
    re.compile(r"\badjacent\s+to\b", re.IGNORECASE),
    re.compile(r"\blinked\s+to\b", re.IGNORECASE),
]

_DEPTH_PATTERN = re.compile(r"\b(?:depth|hops?)\s*[:=]?\s*(\d+)\b|(\d+)\s*hops?\b", re.IGNORECASE)


def detect_intent(text: str) -> str | None:
    """Detects supported intent from text or returns None if ambiguous/unsupported."""
    matches: list[str] = []
    if any(p.search(text) for p in _DOWNSTREAM_PATTERNS):
        matches.append("DOWNSTREAM")
    if any(p.search(text) for p in _UPSTREAM_PATTERNS):
        matches.append("UPSTREAM")
    if any(p.search(text) for p in _NEIGHBORS_PATTERNS):
        matches.append("NEIGHBORS")

    # If exactly one intent matches unambiguously, return it
    if len(matches) == 1:
        return matches[0]
    return None


def extract_depth(text: str) -> int | None:
    """Extracts optional traversal depth parameter from query string."""
    m = _DEPTH_PATTERN.search(text)
    if m:
        depth_val = m.group(1) or m.group(2)
        if depth_val and depth_val.isdigit():
            val = int(depth_val)
            if val > 0:
                return val
    return None


class RuleBasedIntentResolver:
    """Deterministic intent resolver conforming to IntentResolver protocol."""

    def resolve(self, question: str) -> QueryIntent:
        """Parses natural language question into a validated QueryIntent.
        
        Raises ValueError if intent or entity cannot be safely determined.
        """
        if not question or not question.strip():
            raise ValueError("Query question cannot be empty")

        intent = detect_intent(question)
        if intent is None:
            raise ValueError(f"Could not determine a supported query intent from question: {question!r}")

        entity = extract_and_normalize_entity(question)
        if entity is None:
            raise ValueError(f"Could not identify a valid entity reference in question: {question!r}")

        depth = extract_depth(question)
        return QueryIntent(intent=intent, entity=entity, depth=depth)

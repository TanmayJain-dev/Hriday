"""Explicit review state transitions."""
from __future__ import annotations

VALID_TRANSITIONS = {
    "not_required": set(),
    "pending": {"confirmed", "rejected", "corrected"},
    "confirmed": set(),
    "rejected": set(),
    "corrected": set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())

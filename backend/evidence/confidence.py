"""Configurable confidence gate for answer/review routing."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidencePolicy:
    auto_answer_threshold: float = 0.85
    review_threshold: float = 0.60

    def requires_review(self, confidence: float) -> bool:
        return confidence < self.auto_answer_threshold

    def is_blocked(self, confidence: float) -> bool:
        return confidence < self.review_threshold

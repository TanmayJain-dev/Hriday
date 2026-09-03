from __future__ import annotations
from typing import Protocol


class ExtractionProvider(Protocol):
    def extract(self, document: object) -> dict: ...

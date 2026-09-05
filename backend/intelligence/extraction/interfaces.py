from __future__ import annotations
from typing import Protocol

from .models import ExtractionResult

class ExtractionProvider(Protocol):
    def extract(self, document: object) -> ExtractionResult: ...

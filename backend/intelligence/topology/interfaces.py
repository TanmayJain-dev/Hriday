from __future__ import annotations
from typing import Protocol

from backend.intelligence.extraction.models import ExtractionResult

from .models import TopologyResult

class TopologyProvider(Protocol):
    def reconstruct(self, extraction_result: ExtractionResult) -> TopologyResult: ...

from __future__ import annotations
from typing import Protocol

from .models import ExtractionResult

from .models import TopologyResult

class TopologyProvider(Protocol):
    """Stable boundary from extracted visual observations to topology facts."""

    def reconstruct(self, extraction_result: ExtractionResult) -> TopologyResult: ...

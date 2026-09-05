from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import BoundingBox, TextRegion
from .document_loader import LoadedPage


@dataclass(frozen=True)
class OCRResult:
    """Text observations produced by an OCR provider."""

    regions: list[TextRegion]


class OCRProvider(Protocol):
    """Interface implemented by concrete OCR engines."""

    def extract_text(self, page: LoadedPage) -> OCRResult:
        ...


class FixtureOCRProvider:
    """Deterministic OCR provider for development and testing.

    This does not perform real OCR. It allows the extraction
    pipeline and contracts to be tested before an OCR engine
    is selected and integrated.
    """

    def __init__(self, regions: list[TextRegion] | None = None) -> None:
        self._regions = regions or []

    def extract_text(self, page: LoadedPage) -> OCRResult:
        page_regions = [
            region
            for region in self._regions
            if region.page == page.page_number
        ]

        return OCRResult(regions=page_regions)

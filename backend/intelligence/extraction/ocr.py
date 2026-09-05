from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import easyocr

from .document_loader import LoadedPage
from .models import BoundingBox, TextRegion


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
    pipeline and contracts to be tested before a real OCR engine
    is used.
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


class EasyOCROCRProvider:
    """OCR provider backed by EasyOCR."""

    def __init__(
        self,
        languages: list[str] | None = None,
        gpu: bool = False,
    ) -> None:
        self._reader = easyocr.Reader(
            languages or ["en"],
            gpu=gpu,
        )

    def extract_text(self, page: LoadedPage) -> OCRResult:
        detections = self._reader.readtext(page.image_bytes)

        regions: list[TextRegion] = []

        for index, (polygon, text, confidence) in enumerate(detections):
            xs = [point[0] for point in polygon]
            ys = [point[1] for point in polygon]

            bbox = BoundingBox(
                x_min=float(min(xs)),
                y_min=float(min(ys)),
                x_max=float(max(xs)),
                y_max=float(max(ys)),
            )

            regions.append(
                TextRegion(
                    text=text,
                    page=page.page_number,
                    bbox=bbox,
                    confidence=float(confidence),
                )
            )

        return OCRResult(regions=regions)
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentPage:
    """A single document page prepared for downstream extraction."""

    page_number: int
    source_path: str
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class PreprocessingResult:
    """Normalized document information passed to extraction adapters."""

    document_id: str
    pages: list[DocumentPage]


class Preprocessor:
    """Dependency-light preprocessing foundation.

    Actual PDF/image decoding can be provided by a later adapter.
    """

    def preprocess(self, document_path: str | Path) -> PreprocessingResult:
        path = Path(document_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if not path.is_file():
            raise ValueError(f"Document path is not a file: {path}")

        document_id = path.stem

        page = DocumentPage(
            page_number=1,
            source_path=str(path),
        )

        return PreprocessingResult(
            document_id=document_id,
            pages=[page],
        )
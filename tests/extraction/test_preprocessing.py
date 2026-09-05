from pathlib import Path

import pytest

from backend.intelligence.extraction.preprocessing import (
    DocumentPage,
    Preprocessor,
)


def test_preprocessor_creates_document_result(tmp_path: Path) -> None:
    document = tmp_path / "drawing.png"
    document.write_bytes(b"fixture")

    result = Preprocessor().preprocess(document)

    assert result.document_id == "drawing"
    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert result.pages[0].source_path == str(document)


def test_preprocessor_rejects_missing_document(tmp_path: Path) -> None:
    document = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        Preprocessor().preprocess(document)


def test_document_page_stores_page_metadata() -> None:
    page = DocumentPage(
        page_number=2,
        source_path="drawing.pdf",
        width=1920,
        height=1080,
    )

    assert page.page_number == 2
    assert page.source_path == "drawing.pdf"
    assert page.width == 1920
    assert page.height == 1080

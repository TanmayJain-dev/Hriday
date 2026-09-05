from pathlib import Path

import pymupdf
import pytest

from backend.intelligence.extraction.document_loader import DocumentLoader


def create_test_pdf(path: Path) -> None:
    document = pymupdf.open()
    page = document.new_page(width=300, height=200)
    page.insert_text((50, 100), "HRIDAY TEST")
    document.save(path)
    document.close()


def test_load_pdf_returns_rendered_pages(tmp_path: Path) -> None:
    pdf_path = tmp_path / "drawing.pdf"
    create_test_pdf(pdf_path)

    result = DocumentLoader().load(pdf_path)

    assert result.document_id == "drawing"
    assert result.source_path == str(pdf_path)
    assert len(result.pages) == 1

    page = result.pages[0]

    assert page.page_number == 1
    assert page.width > 0
    assert page.height > 0
    assert len(page.image_bytes) > 0


def test_load_image_returns_page(tmp_path: Path) -> None:
    image_path = tmp_path / "drawing.png"

    document = pymupdf.open()
    page = document.new_page(width=100, height=80)
    pixmap = page.get_pixmap()
    pixmap.save(image_path)
    document.close()

    result = DocumentLoader().load(image_path)

    assert result.document_id == "drawing"
    assert len(result.pages) == 1
    assert result.pages[0].width > 0
    assert result.pages[0].height > 0
    assert len(result.pages[0].image_bytes) > 0


def test_loader_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        DocumentLoader().load(tmp_path / "missing.pdf")


def test_loader_rejects_unsupported_file(tmp_path: Path) -> None:
    file_path = tmp_path / "drawing.txt"
    file_path.write_text("not a drawing")

    with pytest.raises(ValueError, match="Unsupported document type"):
        DocumentLoader().load(file_path)

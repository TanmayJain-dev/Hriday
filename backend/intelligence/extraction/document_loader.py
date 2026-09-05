from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pymupdf


SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


@dataclass(frozen=True)
class LoadedPage:
    """A document page available for downstream visual extraction."""

    page_number: int
    width: int
    height: int
    source_path: str
    image_bytes: bytes


@dataclass(frozen=True)
class LoadedDocument:
    """A loaded document and its rendered pages."""

    document_id: str
    source_path: str
    pages: list[LoadedPage]


class DocumentLoader:
    """Load supported PDF and image documents."""

    def load(self, document_path: str | Path) -> LoadedDocument:
        path = Path(document_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if not path.is_file():
            raise ValueError(f"Document path is not a file: {path}")

        extension = path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {extension or '<none>'}"
            )

        if extension == ".pdf":
            return self._load_pdf(path)

        return self._load_image(path)

    def _load_pdf(self, path: Path) -> LoadedDocument:
        pages: list[LoadedPage] = []

        with pymupdf.open(path) as document:
            for index, page in enumerate(document):
                pixmap = page.get_pixmap()
                image_bytes = pixmap.tobytes("png")

                pages.append(
                    LoadedPage(
                        page_number=index + 1,
                        width=pixmap.width,
                        height=pixmap.height,
                        source_path=str(path),
                        image_bytes=image_bytes,
                    )
                )

        return LoadedDocument(
            document_id=path.stem,
            source_path=str(path),
            pages=pages,
        )

    def _load_image(self, path: Path) -> LoadedDocument:
        image_bytes = path.read_bytes()

        with pymupdf.open(path) as document:
            page = document[0]
            pixmap = page.get_pixmap()

        loaded_page = LoadedPage(
            page_number=1,
            width=pixmap.width,
            height=pixmap.height,
            source_path=str(path),
            image_bytes=image_bytes,
        )

        return LoadedDocument(
            document_id=path.stem,
            source_path=str(path),
            pages=[loaded_page],
        )

from unittest.mock import Mock, patch
from backend.intelligence.extraction.document_loader import LoadedPage
from backend.intelligence.extraction.models import BoundingBox, TextRegion
from backend.intelligence.extraction.ocr import (
    EasyOCROCRProvider,
    FixtureOCRProvider,
)


def create_page(page_number: int = 1) -> LoadedPage:
    return LoadedPage(
        page_number=page_number,
        width=1000,
        height=800,
        source_path="fixture.png",
        image_bytes=b"fixture",
    )


def test_fixture_ocr_returns_matching_page_regions() -> None:
    regions = [
        TextRegion(
            text="P-101",
            page=1,
            bbox=BoundingBox(100, 100, 150, 120),
            confidence=0.95,
        ),
        TextRegion(
            text="V-201",
            page=1,
            bbox=BoundingBox(300, 100, 350, 120),
            confidence=0.91,
        ),
    ]

    result = FixtureOCRProvider(regions).extract_text(create_page(1))

    assert len(result.regions) == 2
    assert result.regions[0].text == "P-101"
    assert result.regions[1].text == "V-201"


def test_fixture_ocr_does_not_return_other_pages() -> None:
    regions = [
        TextRegion(
            text="P-101",
            page=1,
            bbox=BoundingBox(100, 100, 150, 120),
            confidence=0.95,
        ),
        TextRegion(
            text="P-202",
            page=2,
            bbox=BoundingBox(200, 200, 250, 220),
            confidence=0.90,
        ),
    ]

    result = FixtureOCRProvider(regions).extract_text(create_page(1))

    assert len(result.regions) == 1
    assert result.regions[0].text == "P-101"


def test_fixture_ocr_preserves_confidence_and_geometry() -> None:
    region = TextRegion(
        text="FT-301",
        page=1,
        bbox=BoundingBox(400, 500, 470, 525),
        confidence=0.87,
    )

    result = FixtureOCRProvider([region]).extract_text(create_page())

    extracted = result.regions[0]

    assert extracted.text == "FT-301"
    assert extracted.confidence == 0.87
    assert extracted.bbox.x_min == 400
    assert extracted.bbox.y_max == 525
@patch("backend.intelligence.extraction.ocr.easyocr.Reader")
def test_easyocr_provider_converts_detection_to_text_region(
    mock_reader: Mock,
) -> None:
    reader = mock_reader.return_value
    reader.readtext.return_value = [
        (
            [[100, 100], [150, 100], [150, 120], [100, 120]],
            "P-101",
            0.96,
        )
    ]

    provider = EasyOCROCRProvider(gpu=False)
    result = provider.extract_text(create_page())

    assert len(result.regions) == 1

    region = result.regions[0]

    assert region.text == "P-101"
    assert region.page == 1
    assert region.confidence == 0.96
    assert region.bbox.x_min == 100
    assert region.bbox.y_min == 100
    assert region.bbox.x_max == 150
    assert region.bbox.y_max == 120


@patch("backend.intelligence.extraction.ocr.easyocr.Reader")
def test_easyocr_provider_initializes_english_reader(
    mock_reader: Mock,
) -> None:
    EasyOCROCRProvider(gpu=False)

    mock_reader.assert_called_once_with(
        ["en"],
        gpu=False,
    )
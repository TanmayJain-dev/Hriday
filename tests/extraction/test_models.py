from backend.intelligence.extraction.models import (
    BoundingBox,
    EntityObservation,
    ExtractionResult,
    LineCandidate,
    TextRegion,
    Uncertainty,
)


def test_extraction_result_has_contract_fields() -> None:
    result = ExtractionResult(document_id="fixture-001")

    data = result.to_dict()

    assert data["document_id"] == "fixture-001"
    assert data["entities"] == []
    assert data["text_regions"] == []
    assert data["line_candidates"] == []
    assert data["uncertainties"] == []


def test_entity_observation_serializes_geometry_and_confidence() -> None:
    entity = EntityObservation(
        entity_id="entity-001",
        entity_type="pump",
        page=1,
        bbox=BoundingBox(10, 20, 50, 80),
        confidence=0.92,
        tag="P-101",
    )

    data = entity.to_dict()

    assert data["id"] == "entity-001"
    assert data["type"] == "pump"
    assert data["tag"] == "P-101"
    assert data["confidence"] == 0.92
    assert data["bbox"]["x_min"] == 10
    assert data["bbox"]["y_max"] == 80


def test_text_region_serializes_ocr_observation() -> None:
    region = TextRegion(
        text="P-101",
        page=1,
        bbox=BoundingBox(100, 200, 150, 220),
        confidence=0.96,
    )

    data = region.to_dict()

    assert data["text"] == "P-101"
    assert data["page"] == 1
    assert data["confidence"] == 0.96


def test_line_candidate_is_observation_not_connectivity() -> None:
    line = LineCandidate(
        line_id="line-001",
        page=1,
        geometry=[
            {"x": 10, "y": 20},
            {"x": 100, "y": 20},
        ],
        confidence=0.88,
    )

    data = line.to_dict()

    assert data["id"] == "line-001"
    assert len(data["geometry"]) == 2
    assert data["confidence"] == 0.88
    assert "source" not in data
    assert "target" not in data


def test_uncertainty_is_preserved() -> None:
    uncertainty = Uncertainty(
        uncertainty_type="ambiguous_tag",
        message="Tag may belong to multiple entities.",
        page=1,
        confidence=0.54,
        related_ids=["entity-001", "entity-002"],
    )

    data = uncertainty.to_dict()

    assert data["type"] == "ambiguous_tag"
    assert data["confidence"] == 0.54
    assert data["related_ids"] == ["entity-001", "entity-002"]

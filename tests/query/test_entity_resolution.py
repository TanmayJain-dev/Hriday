"""Tests for entity normalization and extraction in the query layer."""
from backend.intelligence.query.entity_resolution import (
    extract_and_normalize_entity,
    normalize_entity_reference,
)


def test_normalize_pump_variations():
    assert normalize_entity_reference("pump 101") == "P-101"
    assert normalize_entity_reference("PMP-101") == "P-101"
    assert normalize_entity_reference("P-101") == "P-101"
    assert normalize_entity_reference("pmp 101") == "P-101"
    assert normalize_entity_reference("PUMP-101") == "P-101"


def test_normalize_vessel_variations():
    assert normalize_entity_reference("vessel 101") == "V-101"
    assert normalize_entity_reference("VSL-101") == "V-101"
    assert normalize_entity_reference("V-101") == "V-101"


def test_normalize_exchanger_variations():
    assert normalize_entity_reference("exchanger 101") == "E-101"
    assert normalize_entity_reference("HX-101") == "E-101"
    assert normalize_entity_reference("E-101") == "E-101"


def test_extract_entity_from_natural_language():
    assert extract_and_normalize_entity("What is downstream of P-101?") == "P-101"
    assert extract_and_normalize_entity("What comes after pump 101?") == "P-101"
    assert extract_and_normalize_entity("What is upstream of V-101?") == "V-101"
    assert extract_and_normalize_entity("What is connected to PMP-101?") == "P-101"
    assert extract_and_normalize_entity("What is connected to vessel 201?") == "V-201"
    assert extract_and_normalize_entity("Show equipment linked to HX-101") == "E-101"


def test_extract_entity_non_existent():
    # Never invent entities when none are mentioned
    assert extract_and_normalize_entity("Show plant overview and health") is None
    assert extract_and_normalize_entity("") is None
    assert extract_and_normalize_entity("What is the status?") is None

"""Conservative entity normalization for demo-scale P&IDs."""
from __future__ import annotations
import re

def normalize_entity_reference(value: str) -> str:
    cleaned = value.upper().strip()
    cleaned = re.sub(r"\b(PUMP|PMP)\s*[- ]?", "P-", cleaned)
    cleaned = re.sub(r"\b(VESSEL|VSL)\s*[- ]?", "V-", cleaned)
    cleaned = re.sub(r"\b(EXCHANGER|HX)\s*[- ]?", "E-", cleaned)
    return cleaned.replace(" ", "")

def extract_and_normalize_entity(text: str) -> str | None:
    """Extracts and normalizes the first entity tag mentioned in text.

    Returns normalized tag (e.g. 'P-101') or None if no valid entity reference is found.
    """
    # 1. Look for standard hyphenated P&ID tags (e.g. P-101, V-101, E-101, PMP-101)
    tag_match = re.search(r"\b([A-Z]{1,4}-\d{1,4}[A-Z]?)\b", text, re.IGNORECASE)
    if tag_match:
        return normalize_entity_reference(tag_match.group(1))

    # 2. Look for equipment keyword followed by identifier (e.g. "pump 101", "vessel 102")
    named_match = re.search(
        r"\b(PUMP|PMP|VESSEL|VSL|EXCHANGER|HX|VALVE|VLV|TANK|TK)\s*[- ]?\s*([A-Z0-9]+)\b",
        text,
        re.IGNORECASE,
    )
    if named_match:
        return normalize_entity_reference(named_match.group(0))

    return None

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


def extract_all_entities(text: str) -> list[str]:
    """Extracts and normalizes all entity tags mentioned in text, preserving order."""
    results: list[str] = []
    seen: set[str] = set()

    pattern = re.compile(
        r"\b([A-Z]{1,4}-\d{1,4}[A-Z]?)\b|"
        r"\b((?:PUMP|PMP|VESSEL|VSL|EXCHANGER|HX|VALVE|VLV|TANK|TK)\s*[- ]?\s*[A-Z0-9]+)\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        raw = match.group(1) or match.group(2)
        if raw:
            normalized = normalize_entity_reference(raw)
            if normalized not in seen:
                seen.add(normalized)
                results.append(normalized)
    return results


def extract_source_and_target(text: str) -> tuple[str | None, str | None]:
    """Extracts source and target entity references for paths-between queries."""
    rel_match = re.search(
        r"\b(?:between|from)\s+([A-Za-z0-9- ]+?)\s+(?:and|to)\s+([A-Za-z0-9- ]+)",
        text,
        re.IGNORECASE,
    )
    if rel_match:
        src = extract_and_normalize_entity(rel_match.group(1))
        tgt = extract_and_normalize_entity(rel_match.group(2))
        if src and tgt:
            return src, tgt

    all_ents = extract_all_entities(text)
    if len(all_ents) >= 2:
        return all_ents[0], all_ents[1]
    if len(all_ents) == 1:
        return all_ents[0], None
    return None, None

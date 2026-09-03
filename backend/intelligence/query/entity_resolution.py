"""Conservative entity resolution for demo-scale P&IDs."""
import re


def normalize_entity_reference(value: str) -> str:
    cleaned = value.upper().strip()
    cleaned = re.sub(r"\b(PUMP|PMP)\s*[- ]?", "P-", cleaned)
    cleaned = re.sub(r"\b(VESSEL|VSL)\s*[- ]?", "V-", cleaned)
    cleaned = re.sub(r"\b(EXCHANGER|HX)\s*[- ]?", "E-", cleaned)
    return cleaned.replace(" ", "")

"""Small explicit rule checks; expand only when backed by domain requirements."""


def validate_candidate_edge(edge: dict) -> list[str]:
    violations: list[str] = []
    if edge.get("source") == edge.get("target"):
        violations.append("self_connection")
    confidence = float(edge.get("confidence", 1.0))
    if not 0.0 <= confidence <= 1.0:
        violations.append("invalid_confidence")
    if edge.get("requires_verification") and not edge.get("reason"):
        violations.append("review_reason_missing")
    return violations

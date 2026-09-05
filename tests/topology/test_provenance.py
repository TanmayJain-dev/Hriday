from backend.intelligence.topology.models import (
    ExtractionResult,
    JunctionCandidate,
    LineCandidate,
    Point,
)
from backend.intelligence.topology.crossings import (
    CrossingClassificationConfig,
    CrossingKind,
    classify_crossings,
)
from backend.intelligence.topology.junctions import (
    JunctionMatchingConfig,
    reconstruct_junctions,
)


def test_overlap_classification_has_conservative_confidence_and_evidence():
    extraction = ExtractionResult(
        document_id="synthetic-provenance-overlap",
        line_candidates=(
            LineCandidate("L-001", Point(0, 0), Point(10, 0), 0.8, evidence_ids=("a",)),
            LineCandidate("L-002", Point(5, 0), Point(15, 0), 0.6, evidence_ids=("b",)),
        ),
    )

    classification = classify_crossings(
        extraction, CrossingClassificationConfig(0.001)
    )[0]
    assert classification.kind is CrossingKind.COLLINEAR_OVERLAP
    assert classification.confidence == 0.6
    assert classification.evidence_ids == ("a", "b")


def test_junction_uncertainty_preserves_candidate_provenance_and_confidence():
    extraction = ExtractionResult(
        document_id="synthetic-provenance-junction",
        line_candidates=(
            LineCandidate("L-001", Point(0, 0), Point(10, 0), 0.9, evidence_ids=("line",)),
        ),
        junction_candidates=(
            JunctionCandidate("J-1", Point(5, 0), 0.7, evidence_ids=("junction",)),
        ),
    )

    result = reconstruct_junctions(extraction, JunctionMatchingConfig(0.001))
    uncertainty = result.uncertainties[0]
    assert uncertainty["confidence"] == 0.7
    assert uncertainty["evidence_ids"] == ["junction"]
    assert uncertainty["requires_verification"] is True


def test_ambiguous_crossing_confidence_cannot_exceed_line_confidence():

    extraction = ExtractionResult(
        document_id="synthetic-provenance-ambiguous",
        line_candidates=(
            LineCandidate("L-001", Point(0, 0), Point(10, 10), 0.4),
            LineCandidate("L-002", Point(0, 10), Point(10, 0), 0.6),
        ),
        junction_candidates=(
            JunctionCandidate(
                "J-1",
                Point(5, 5),
                0.95,
                attributes={"classification": "crossing"},
            ),
        ),
    )

    classification = classify_crossings(
        extraction, CrossingClassificationConfig(0.001)
    )[0]
    assert classification.confidence == 0.4
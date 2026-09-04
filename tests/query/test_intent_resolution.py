"""Tests for query intent resolution."""
import pytest
from backend.intelligence.query.intent_resolution import RuleBasedIntentResolver
from backend.intelligence.query.models import QueryIntent


@pytest.fixture
def resolver() -> RuleBasedIntentResolver:
    return RuleBasedIntentResolver()


def test_downstream_intent_resolution(resolver: RuleBasedIntentResolver):
    q1 = "What is downstream of P-101?"
    intent1 = resolver.resolve(q1)
    assert intent1 == QueryIntent(intent="DOWNSTREAM", entity="P-101", depth=None)

    q2 = "What comes after pump 101?"
    intent2 = resolver.resolve(q2)
    assert intent2 == QueryIntent(intent="DOWNSTREAM", entity="P-101", depth=None)

    q3 = "What flows into from PMP-101?"
    intent3 = resolver.resolve(q3)
    assert intent3.intent == "DOWNSTREAM"
    assert intent3.entity == "P-101"


def test_upstream_intent_resolution(resolver: RuleBasedIntentResolver):
    q1 = "What is upstream of V-101?"
    intent1 = resolver.resolve(q1)
    assert intent1 == QueryIntent(intent="UPSTREAM", entity="V-101", depth=None)

    q2 = "What comes before pump 101?"
    intent2 = resolver.resolve(q2)
    assert intent2 == QueryIntent(intent="UPSTREAM", entity="P-101", depth=None)

    q3 = "What is V-101 fed by?"
    intent3 = resolver.resolve(q3)
    assert intent3.intent == "UPSTREAM"
    assert intent3.entity == "V-101"


def test_neighbors_intent_resolution(resolver: RuleBasedIntentResolver):
    q1 = "What is connected to P-101?"
    intent1 = resolver.resolve(q1)
    assert intent1 == QueryIntent(intent="NEIGHBORS", entity="P-101", depth=None)

    q2 = "What are the neighbors of vessel 101?"
    intent2 = resolver.resolve(q2)
    assert intent2 == QueryIntent(intent="NEIGHBORS", entity="V-101", depth=None)


def test_depth_resolution(resolver: RuleBasedIntentResolver):
    q = "What is downstream of P-101 within 2 hops?"
    intent = resolver.resolve(q)
    assert intent.depth == 2

    q_depth = "What is downstream of P-101 with depth 3?"
    intent_depth = resolver.resolve(q_depth)
    assert intent_depth.depth == 3


def test_unsupported_questions_fail_safely(resolver: RuleBasedIntentResolver):
    with pytest.raises(ValueError, match="Could not determine a supported query intent"):
        resolver.resolve("What is the cost of pump 101?")

    with pytest.raises(ValueError, match="Could not determine a supported query intent"):
        resolver.resolve("Can you operate valve V-101?")

    with pytest.raises(ValueError, match="Query question cannot be empty"):
        resolver.resolve("   ")


def test_missing_entity_fails_safely(resolver: RuleBasedIntentResolver):
    with pytest.raises(ValueError, match="Could not identify a valid entity reference"):
        resolver.resolve("What is downstream?")


def test_ambiguous_conflicting_intents_fail_safely(resolver: RuleBasedIntentResolver):
    # If a question ambiguously asks for both downstream and upstream
    with pytest.raises(ValueError, match="Could not determine a supported query intent"):
        resolver.resolve("What is downstream and upstream of P-101?")


def test_paths_between_intent_resolution(resolver: RuleBasedIntentResolver):
    q1 = "What is the path between P-101 and V-102?"
    intent1 = resolver.resolve(q1)
    assert intent1 == QueryIntent(intent="PATHS_BETWEEN", entity="P-101", target_entity="V-102", depth=None)

    q2 = "How to get from pump 101 to vessel 102?"
    intent2 = resolver.resolve(q2)
    assert intent2.intent == "PATHS_BETWEEN"
    assert intent2.entity == "P-101"
    assert intent2.target_entity == "V-102"

    with pytest.raises(ValueError, match="Paths-between query requires both source and target"):
        resolver.resolve("What is the path between P-101?")

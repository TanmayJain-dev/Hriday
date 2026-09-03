# HRIDAY

> Sovereign Industrial AI — from P&ID pixels to verifiable engineering knowledge.

**Team GARUD · Smart India Hackathon 2026 · SIH26117 · MRPL**

HRIDAY is a sovereign, on-premise, agentic AI workbench for confidential industrial engineering work. Its flagship MVP transforms a supported P&ID drawing into a topology-aware engineering graph that engineers can query in natural language, with evidence, confidence, provenance, and human verification attached to important results.

## The core idea

```text
CONFIDENTIAL P&ID
      ↓
VISUAL PERCEPTION
      ↓
STRUCTURED EVIDENCE
      ↓
TOPOLOGY RECONSTRUCTION
      ↓
ENGINEERING GRAPH
      ↓
CONSTRAINED LOCAL AGENT
      ↓
EVIDENCE-BACKED ANSWER
      ↓
CONFIDENCE GATE → HUMAN REVIEW when required
```

**Vision sees. Topology connects. Graph stores truth. Agent queries. Evidence explains. Human verifies uncertainty.**

The LLM is not the source of truth for plant connectivity.

## Why a P&ID is different from an ordinary PDF

A conventional document assistant can retrieve text. A P&ID encodes relationships through geometry, symbols, lines, junctions, crossings, labels and direction. Two nearby labels can be unrelated; two distant objects can be connected by a thin line; a crossing can be a connection or two independent paths.

HRIDAY therefore does not reduce the problem to `PDF → OCR → chunks → LLM`. It separates observation from topology interpretation and persists supported relationships as a provenance-aware graph.

## Architecture at a glance

```text
Frontend
   │ HTTP / JSON
   ▼
FastAPI API
   │
   ▼
Orchestration Pipeline
   │
   ├── Ingestion
   ├── Extraction
   ├── Topology
   ├── Graph
   ├── Query / Agent
   ├── Evidence
   └── Verification
```

Contract flow:

```text
DocumentInput
   ↓
ExtractionResult
   ↓
TopologyResult
   ↓
GraphResult
   ↓
QueryIntent + GraphResult
   ↓
Evidence-backed Answer
```

## The truth hierarchy

```text
1. Visual evidence
2. Deterministic geometric observations
3. Domain validation rules
4. Reconstructed topology
5. Graph facts
6. Retrieved graph results
7. LLM explanation
```

**Never reverse this hierarchy.**

## What the LLM can and cannot do

### Allowed

- understand natural-language intent
- resolve aliases such as “pump 101” → `P-101`
- choose constrained read-only graph tools
- formulate graph queries
- explain retrieved facts and evidence

### Forbidden

- invent connectivity
- fabricate evidence
- create unsupported edges
- silently override graph facts
- suppress uncertainty
- actuate equipment
- approve LOTO or operational safety actions
- make autonomous plant-control decisions

**Architectural rule: the model explains retrieved truth; it does not manufacture it.**

## Flagship MVP

The prototype intentionally proves one difficult vertical slice:

```text
P&ID upload
   ↓
Extraction
   ↓
Topology reconstruction
   ↓
Engineering graph
   ↓
Natural-language query
   ↓
Highlighted source evidence
   ↓
Confidence gate
   ↓
Human verification when required
```

### Golden demo

> **“What is downstream of P-101?”**

The deterministic graph should be able to return a path such as:

```text
P-101 → E-101 → V-102
```

A deliberately ambiguous crossing should instead become a reviewable state such as:

```text
Confidence: 0.62
Human verification required.
```

That behavior is intentional. In an industrial context, visible uncertainty is better than a fluent unsupported answer.

## Why the repository is structured this way

Six developers — often using AI coding agents — need to work in parallel without sharing one giant monolith.

`contracts/` is the constitution. Domain ownership is explicit. Subsystems exchange typed, documented results. Fixtures make upstream and downstream work independently testable. Graph storage is abstracted so the MVP can stay simple while remaining compatible with a future Neo4j implementation.

### Intended role packages

| Member | Package |
|---|---|
| 1 | Core architecture, graph, orchestration, integration |
| 2 | Frontend and visualization |
| 3 | Visual extraction |
| 4 | Topology reconstruction |
| 5 | Agent and tool integration |
| 6 | Evidence and human verification |

Identities are intentionally unassigned until the team meeting.

## Engineering principles

```text
Small modules.
Stable contracts.
Deterministic facts.
Explicit uncertainty.
Read-only agent tools.
Evidence attached to claims.
Tests around hard algorithms.
No silent architectural drift.
```

## Research foundation

HRIDAY builds on complementary work in engineering-diagram digitization, P&ID-specific validation, relational and hyper-relational extraction, explicit topology reconstruction, and graph-based P&ID interaction. Research notes and the rationale for the architecture live in `docs/research/` and `docs/decisions/`.

External research metrics are never HRIDAY results.

## Evaluation

Every metric must be labeled as one of:

- **Target** — intended objective.
- **Measured** — obtained from a defined HRIDAY experiment.
- **Paper Result** — reported by external research.

The benchmark focuses on extraction, junction/crossing behavior, topology edges, graph-path correctness, evidence attribution, unsupported-claim rate, human-review/correction behavior, and defined manual-tracing tasks.

## Security boundary

The MVP is read-only with respect to industrial systems and is designed for local/on-premise deployment. Real confidential P&IDs must never be committed to the repository; use synthetic or sanitized fixtures instead.

This is a prototype security posture, not a production certification.

## Development with AI agents

An AI coding agent should be able to work from the repository itself. Start here:

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `docs/development/AI_AGENT_GUIDE.md`
4. `docs/development/member-X.md`
5. the relevant contracts

The agent must respect ownership, preserve contracts, test changes, inspect diffs, and report architectural blockers rather than inventing cross-domain fixes.

## Development path

```text
Architecture + contracts
        ↓
Contract-valid mocked pipeline
        ↓
Real extraction
        ↓
Real topology
        ↓
Graph querying
        ↓
Evidence + HITL
        ↓
Integration + demo polish
```

The prototype is deliberately narrow. It does not attempt full DEXPI conformance, an exhaustive ISA-5.1 ontology, custom foundation-model training, plant control, autonomous HAZOP/LOTO decisions, or broad enterprise document RAG.

## Repository map

```text
backend/     → FastAPI + intelligence pipeline
frontend/    → engineer-facing visualization
contracts/   → protected subsystem interfaces
data/        → synthetic fixtures only
docs/        → architecture, roles, research, decisions, evaluation
scripts/     → local validation and demo entry points
tests/       → domain and integration tests
```

## Team naming

**GARUD** = team.

**HRIDAY** = project.

## Status

**Architecture + executable bootstrap.** The repository contains the project constitution, domain boundaries, contracts, demo fixtures, initial graph/query/evidence primitives, and CI scaffolding. Implementation work should replace or extend these pieces through the documented interfaces.

## License

Final licensing will be selected after confirming SIH requirements and the licenses of third-party models, datasets, and dependencies.

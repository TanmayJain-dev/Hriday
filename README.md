# HRIDAY

> **Sovereign Industrial AI — from P&ID pixels to verifiable engineering knowledge.**

**Team GARUD · Smart India Hackathon 2026 · SIH26117 · MRPL**

HRIDAY is a sovereign, on-premise, agentic AI workbench for confidential industrial engineering work. Its flagship MVP transforms a supported P&ID drawing into a topology-aware engineering graph that engineers can query in natural language, with visual evidence, confidence, provenance, and human verification attached to important claims.

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

The LLM is **not** the source of truth for plant connectivity.

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

## Truth hierarchy

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

The prototype deliberately proves one difficult vertical slice:

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

A deliberately ambiguous crossing should instead become a reviewable state:

```text
Confidence: 0.62
Human verification required.
```

That behavior is intentional. In an industrial context, visible uncertainty is better than a fluent unsupported answer.

## What makes the architecture different

### 01 — Topology-first

Connectivity is reconstructed explicitly from geometry, endpoints, junction logic and engineering rules rather than inferred from text proximity.

### 02 — Evidence is first-class

A graph edge can retain the source document, page, region, supporting observation, confidence and validation path that support the claim.

### 03 — Uncertainty is actionable

Ambiguous interpretations remain ambiguous. They can become review items, be confirmed/rejected/corrected, and leave a provenance trail.

### 04 — Sovereign by design

The intended deployment boundary is local/on-premise. Sensitive drawings do not need to leave the controlled environment.

### 05 — Model-agnostic interfaces

OCR, object detection, multimodal models and graph stores sit behind replaceable boundaries. The architecture is built around contracts rather than one vendor.

## Six-person development model

This repository is deliberately structured so six developers — including AI coding agents — can work in parallel without turning the project into a merge-conflict monolith.

| Role | Primary domain |
|---|---|
| Member 1 | Core architecture, graph, orchestration, integration |
| Member 2 | Frontend and visualization |
| Member 3 | Visual extraction |
| Member 4 | Topology reconstruction |
| Member 5 | Agent and tool integration |
| Member 6 | Evidence and human verification |

**Assignments are intentionally open until the team meeting.** The repository already contains the role packages so tomorrow's decision changes ownership, not architecture.

## The contract principle

`contracts/` is the constitution.

Subsystems should communicate through stable structures such as:

```text
DocumentInput
ExtractionResult
TopologyResult
GraphResult
QueryIntent
EvidenceReference
VerificationDecision
Answer
```

This means an internal extraction implementation can change without forcing the topology engineer to rewrite their code, and a future Neo4j adapter can replace the prototype graph backend without rewriting the query semantics.

## Repository map

```text
backend/
  api/                 FastAPI entry point and integration routes
  orchestration/       stage-oriented pipeline
  intelligence/
    extraction/        observations from documents
    topology/          geometric connectivity reconstruction
    graph/             canonical graph facts + GraphStore
    query/             constrained query semantics + agent boundary
  evidence/            source mapping and confidence
  verification/        human-review state machine

frontend/              engineer-facing UI
contracts/             protected JSON Schemas
 data/                 synthetic fixtures only
docs/                  architecture, research, roles, decisions, evaluation
scripts/               validation and demo helpers
tests/                 domain + integration tests
```

## Graph philosophy

The graph is not a decorative visualization. It is the deterministic query substrate.

For the MVP, an in-process store is preferred for simplicity:

```text
GraphStore
├── prototype in-memory implementation
└── future NetworkX / Neo4j adapters
```

The graph layer owns traversal semantics such as upstream, downstream and neighborhood queries. The agent does not get to redefine those semantics.

## Evidence and verification philosophy

Every material engineering claim should be capable of answering:

> **Why do we believe this?**

Conceptually:

```text
pixels
  ↓
observation
  ↓
interpretation
  ↓
graph fact
  ↓
query result
  ↓
evidence-backed answer
```

When uncertainty exceeds the configured confidence policy:

```text
AUTO_GENERATED
      ↓
confidence gate
      ↓
REVIEW_REQUIRED
      ↓
CONFIRM / REJECT / EDIT
      ↓
updated graph state + provenance
```

## Research foundation

HRIDAY builds on complementary research in engineering-diagram digitization, P&ID-specific validation, hyper-relational diagram extraction, explicit topology reconstruction, and GraphRAG-based P&ID interaction.

The repository does **not** treat any single paper as solving the complete HRIDAY problem. The research informs separate stages that we integrate into one sovereign, evidence-linked workflow.

See `docs/research/README.md`.

## Evaluation discipline

Every metric reported by the project must be labeled:

- **Target** — intended objective, not yet measured.
- **Measured** — obtained from a defined reproducible HRIDAY experiment.
- **Paper Result** — reported by external research.

Never present a paper's accuracy as HRIDAY's accuracy.

## Security boundary

The MVP is read-only with respect to industrial systems and is designed for local/on-premise execution. Real confidential P&IDs and sensitive engineering data must never be committed to this repository.

Use synthetic or sanitized fixtures in `data/`.

This is a prototype security posture, not a production security certification.

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

### Explicitly deferred

- full DEXPI conformance
- exhaustive ISA-5.1 ontology
- custom foundation-model training
- production-scale distributed processing
- plant control/integration
- autonomous HAZOP/LOTO decisions
- broad enterprise document RAG
- cloud-only dependencies

We are trying to prove one difficult vertical slice exceptionally well.

## AI-agent entry point

A coding agent should be able to enter the repository and understand its mission without a separate project prompt.

Read in order:

```text
AGENTS.md
    ↓
ARCHITECTURE.md
    ↓
docs/development/AI_AGENT_GUIDE.md
    ↓
docs/development/member-X.md
    ↓
relevant contracts
```

The agent must respect its ownership boundary, preserve contracts, test non-trivial behavior, inspect diffs, and report cross-domain blockers rather than silently rewriting other people's work.

## Safe Git workflow

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feature/member-X-<domain>

# work + test

git status
git diff --check
git diff

git add <only-your-files>
git diff --cached
git commit -m "feat(domain): explain the change"
git push -u origin feature/member-X-<domain>
```

Never force-push shared work. Never use destructive cleanup commands to solve an ordinary merge problem.

## Project identity

**GARUD** = team.

**HRIDAY** = project.

**SIH26117** = software problem statement.

**MRPL** = sponsor/context.

## Status

**Architecture + executable bootstrap.** The repository is ready for the team's role-assignment meeting and for parallel implementation.

## License

Final licensing will be selected after confirming SIH requirements and third-party model, dataset and dependency licenses.

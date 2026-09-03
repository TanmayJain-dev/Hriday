# HRIDAY

Sovereign Industrial AI — from P&ID pixels to verifiable engineering knowledge.

**Team GARUD · SIH 2026 · SIH26117 · MRPL**

HRIDAY is a sovereign, on-premise, agentic AI workbench for confidential industrial engineering work. The flagship MVP transforms a supported P&ID drawing into a topology-aware engineering graph that engineers can query in natural language, with visual evidence, confidence, provenance, and human verification attached to important claims.

## Core invariant

> **Vision sees. Topology connects. Graph stores truth. Agent queries. Evidence explains. Human verifies uncertainty.**

The LLM is not the source of truth for plant connectivity.

## Why P&IDs need a different approach

A P&ID is not an ordinary PDF. Meaning is encoded in geometry, symbols, linework, junctions, crossings, labels and direction. Semantic proximity is not physical connectivity.

HRIDAY therefore does not collapse the problem into `PDF → OCR → chunks → LLM`. It separates visual observation from topological interpretation and persists supported relationships as graph facts with provenance.

## System pipeline

```text
P&ID PDF / PNG / SCAN
        ↓
Visual Perception
(OpenCV / OCR / detector / local VLM)
        ↓
Structured Evidence
(objects · tags · geometry · line candidates)
        ↓
Topology Reconstruction
(geometry · endpoints · junctions · crossings · rules)
        ↓
Engineering Graph
(nodes · relationships · provenance · confidence)
        ↓
Constrained Local Agent
(intent · entity resolution · read-only graph tools)
        ↓
Evidence-backed Answer
(graph path · source region · confidence)
        ↓
Confidence Gate
        ├── high confidence → answer
        └── uncertain → human verification → graph correction
```

## The LLM boundary

### The local model may

- understand natural-language intent;
- resolve references such as “pump 101” to `P-101`;
- select constrained, read-only graph tools;
- formulate graph queries;
- explain retrieved facts and evidence.

### The local model may not

- invent connectivity;
- fabricate evidence;
- silently create unsupported graph edges;
- suppress uncertainty;
- actuate equipment;
- approve LOTO or operational safety actions;
- make autonomous plant-control decisions.

**The model explains retrieved truth. It does not manufacture it.**

## Flagship MVP

The first demonstrable vertical slice is intentionally narrow:

```text
Upload P&ID
   ↓
Extract supported entities and line candidates
   ↓
Reconstruct supported topology
   ↓
Build provenance-aware graph
   ↓
Ask: “What is downstream of P-101?”
   ↓
Return deterministic graph path
   ↓
Highlight source evidence
   ↓
Show confidence
   ↓
Escalate ambiguity to human review
```

A deliberate ambiguous crossing is a feature of the demo: HRIDAY should say **“please verify”** rather than silently guessing.

## Repository architecture

```text
backend/
  api/                 FastAPI entry point + integration routes
  orchestration/       stage-oriented pipeline
  intelligence/
    extraction/        visual observations
    topology/          geometric connectivity reconstruction
    graph/             canonical graph facts + GraphStore
    query/             constrained intent/tool semantics
  evidence/            source mapping + confidence
  verification/        human-review state machine

frontend/              engineer-facing visualization
contracts/             protected subsystem interfaces
data/                  synthetic/sanitized fixtures only
docs/                  architecture, research, roles, decisions, evaluation
scripts/               validation + demo helpers
tests/                 domain + integration tests
```

### Contracts are the constitution

The subsystem chain is:

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

Internal implementations may change without forcing other domains to rewrite themselves.

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

Never reverse this hierarchy.

## Graph philosophy

The graph is not a decorative visualization. It is the deterministic query substrate.

The MVP uses a small, replaceable `GraphStore` boundary. An in-process implementation is the default path for the prototype; future NetworkX/Neo4j adapters can sit behind the same interface.

## Evidence + verification

Every material claim should be able to answer:

> **Why do we believe this?**

Conceptually:

```text
pixels → observation → interpretation → graph fact → query result → answer
```

Confidence is a control signal, not a UI ornament:

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

## Six-person team model

Assignments are deliberately left open until the team meeting. The repository contains role packages so the team can assign people without changing the architecture.

| Member | Domain package |
|---|---|
| 1 | Core architecture, graph, orchestration, integration |
| 2 | Frontend + visualization |
| 3 | Visual extraction |
| 4 | Topology reconstruction |
| 5 | Agent + tool integration |
| 6 | Evidence + human verification |

## Research foundation

HRIDAY integrates complementary research directions in engineering-diagram digitization, P&ID-specific validation, hyper-relational extraction, explicit topology reconstruction, and GraphRAG-based interaction.

We do not claim that one paper solves the entire problem, and external paper metrics are never presented as HRIDAY measurements.

See `docs/research/README.md` and `docs/decisions/`.

## Evaluation discipline

Every reported result must be labeled:

- **Target** — intended objective;
- **Measured** — obtained from a defined HRIDAY experiment;
- **Paper Result** — reported by external research.

Never present target numbers or paper numbers as achieved HRIDAY performance.

## Security boundary

The intended deployment model is local/on-premise. The MVP is read-only with respect to industrial systems.

Real confidential P&IDs and engineering records must never enter version control. Use synthetic or sanitized fixtures only.

This is a prototype security posture, not a production certification.

## Explicitly deferred

- full DEXPI conformance;
- exhaustive ISA-5.1 ontology;
- custom foundation-model training;
- production-scale distributed infrastructure;
- plant control/integration;
- autonomous HAZOP/LOTO decisions;
- broad enterprise document RAG;
- cloud-only dependencies.

The goal is one difficult vertical slice implemented exceptionally well.

## AI-agent entry point

A coding agent should not require a second project prompt.

Read:

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

Agents must respect ownership, preserve contracts, test non-trivial behavior, inspect diffs, and report cross-domain blockers instead of rewriting another subsystem.

## Development workflow

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feature/member-X-<domain>

# implement + test

git status
git diff --check
git diff
git add <only-your-files>
git diff --cached
git commit -m "feat(domain): describe the change"
git push -u origin feature/member-X-<domain>
```

Never force-push shared work. Never use destructive cleanup commands to solve normal merge problems.

## Status

**Architecture + executable bootstrap.** The repository is prepared for tomorrow’s role-assignment meeting and parallel implementation.

## Naming

**GARUD** = team.

**HRIDAY** = project.

**SIH26117** = software problem statement.

**MRPL** = sponsor/context.

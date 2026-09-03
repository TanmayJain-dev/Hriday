# HRIDAY

> **Sovereign Industrial AI — from P&ID pixels to verifiable engineering knowledge.**

**Team GARUD · Smart India Hackathon 2026 · SIH26117 · MRPL**

HRIDAY is a **sovereign, on-premise, agentic AI workbench for confidential industrial engineering work**. Its flagship MVP turns a legacy Piping & Instrumentation Diagram (P&ID) into a topology-aware engineering graph that an engineer can query in natural language — while keeping visual evidence, confidence, provenance, and human verification attached to the result.

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

## Why this is not “chat with PDF”

A P&ID is a relational engineering system, not merely a text document. Proximity is not connectivity; thin process lines, crossings, junctions, labels and directionality carry relationships that ordinary semantic chunking cannot safely recover.

HRIDAY therefore separates observation from interpretation and persists supported relationships as a graph with provenance.

## What makes the architecture defensible

- **Topology-first:** connectivity is explicitly reconstructed from geometry, endpoints, junction logic and engineering rules.
- **Evidence-first:** material claims retain page/region references and supporting confidence.
- **Uncertainty-aware:** ambiguous results remain ambiguous and can enter human review.
- **Sovereign:** the target deployment boundary is local/on-premise with no architectural requirement for external AI APIs.
- **Model-agnostic:** visual models, OCR providers and graph stores sit behind interfaces and contracts.

## LLM boundary

The local model may understand intent, resolve aliases, choose read-only graph tools and explain retrieved evidence.

It may **not** invent connectivity, fabricate evidence, silently override graph facts, suppress uncertainty, actuate equipment, approve LOTO/operations, or make autonomous plant-control decisions.

## Flagship MVP

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
Highlighted evidence
   ↓
Confidence gate
   ↓
Human verification when required
```

### Golden demo

> **“What is downstream of P-101?”**

Expected deterministic result on the demo fixture:

```text
P-101 → E-101 → V-102
```

A deliberately ambiguous crossing should instead produce a review state rather than an invented edge.

## Architecture

```text
Frontend
   │
   ▼
FastAPI
   │
   ▼
Orchestration
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
QueryIntent / GraphResult
   ↓
Evidence-backed Answer
```

See `ARCHITECTURE.md`, `AGENTS.md`, `docs/architecture/`, and `contracts/`.

## Repository design

This repository is deliberately structured so six developers — many working through AI coding agents — can work in parallel without sharing a giant monolith.

`contracts/` is the constitution. Folder ownership is explicit. Domain code stays near the domain. Fixtures allow subsystems to progress independently before the full perception stack is complete.

### Intended ownership packages

| Member | Domain package |
|---|---|
| 1 | Core architecture, graph, orchestration, integration |
| 2 | Frontend and visualization |
| 3 | Visual extraction |
| 4 | Topology reconstruction |
| 5 | Agent/tool integration |
| 6 | Evidence and human verification |

Member identities are intentionally unassigned until the team meeting.

## Truth hierarchy

```text
1. Visual evidence
2. Deterministic geometric observation
3. Domain validation rule
4. Reconstructed topology
5. Graph fact
6. Retrieved graph result
7. LLM explanation
```

**Never reverse this hierarchy.**

## Safety boundary

The MVP is a **read-only engineering intelligence and verification workbench**. It is not a plant control system, safety interlock, LOTO approval system, autonomous operations platform, or substitute for engineering judgment.

## Research foundation

HRIDAY builds on complementary research in engineering-diagram digitization, P&ID-specific validation, relational/hyper-relational diagram extraction, explicit topology reconstruction, and GraphRAG-based P&ID interaction. See `docs/research/README.md` for the curated research direction.

## Evaluation

Every number must be labeled as **Target**, **Measured**, or **Paper Result**. Never present a research-paper metric as HRIDAY performance.

Metrics include extraction accuracy, junction/crossing accuracy, graph-path accuracy, evidence attribution, unsupported-claim rate, review/correction rate and defined manual-tracing time reduction.

## Development principles

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

## AI-agent entry point

AI coding agents should read, in order:

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `docs/development/AI_AGENT_GUIDE.md`
4. their `docs/development/member-X.md`
5. relevant contracts

No separate project prompt should be necessary for ordinary implementation work.

## Current status

**Architecture + executable bootstrap.** The repository intentionally starts with fixtures, interfaces, a deterministic in-process graph implementation, validation scripts and agent-safe development rules. Real perception providers can be added behind the same contracts.

## Team naming

**GARUD** = team.

**HRIDAY** = project.

## License

Final licensing will be selected deliberately after confirming SIH requirements and the licenses of third-party models, datasets, and dependencies.

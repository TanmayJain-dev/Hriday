# HRIDAY

> **Sovereign Industrial AI — from P&ID pixels to verifiable engineering knowledge.**

**Team GARUD · Smart India Hackathon 2026 · SIH26117 · MRPL**

HRIDAY is a **sovereign, on-premise, agentic AI workbench for confidential industrial engineering work**. Its flagship MVP turns a legacy Piping & Instrumentation Diagram (P&ID) into a topology-aware engineering graph that an engineer can query in natural language — while keeping visual evidence, confidence, provenance, and human verification attached to the result.

---

## The idea in one picture

```text
                 CONFIDENTIAL P&ID
              PDF / PNG / SCAN / IMAGE
                         │
                         ▼
              ┌──────────────────────┐
              │   VISUAL PERCEPTION  │
              │ OpenCV · OCR · YOLO  │
              │      · local VLM     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  STRUCTURED EVIDENCE │
              │ objects · tags ·     │
              │ text · coordinates · │
              │ line candidates      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ TOPOLOGY ENGINE      │
              │ geometry · junctions │
              │ crossings · rules    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ ENGINEERING GRAPH    │
              │ entities · edges ·   │
              │ provenance · scores  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ LOCAL AGENT          │
              │ intent → entity →    │
              │ constrained graph    │
              │ query → explanation  │
              └──────────┬───────────┘
                         │
                         ▼
          ┌───────────────────────────────┐
          │  EVIDENCE-BACKED ANSWER      │
          │  graph path + source region  │
          │  + confidence + provenance   │
          └──────────────┬────────────────┘
                         │
                 confidence gate
                  ┌──────┴──────┐
                  │             │
                 HIGH          LOW
                  │             │
                  ▼             ▼
               ANSWER      HUMAN REVIEW
                                  │
                                  ▼
                           GRAPH CORRECTION
```

### The core principle

**Vision sees. Topology connects. Graph stores truth. Agent queries. Evidence explains. Human verifies uncertainty.**

The LLM is **not** the source of truth for plant connectivity.

---

## Why P&IDs are not ordinary PDFs

A normal document assistant can find text near a phrase. A P&ID asks a different question:

> **What is physically / logically connected to what?**

Two labels can be centimetres apart yet have no process connection. Two distant objects can be connected by a thin line. A crossing may be a junction — or may simply be two lines passing over one another.

That is why HRIDAY does **not** reduce the problem to `PDF → OCR → chunks → LLM`.

Instead, HRIDAY separates **visual observation** from **topological interpretation**, then persists the result as a graph with evidence.

---

## What makes HRIDAY different

### 01 — Topology-first

Connectivity is reconstructed explicitly from geometry, junctions, line candidates, and engineering constraints rather than inferred from text proximity.

### 02 — Evidence is first-class

A graph edge is not merely `P-101 → E-101`. It can retain the page, region, source observation, confidence, and validation path that support that claim.

### 03 — Uncertainty is visible

Ambiguous interpretations do not become silent guesses. Low-confidence results are surfaced for human verification.

### 04 — Sovereign by design

The intended deployment boundary is local/on-premise. Sensitive P&IDs and engineering context do not need to leave the controlled environment.

### 05 — Model-agnostic architecture

The multimodal model, OCR backend, object detector, and graph store sit behind replaceable interfaces. The system is designed around contracts, not one vendor.

---

## What the LLM does — and does not do

### The LLM may

- understand natural-language engineering questions
- resolve aliases such as “pump 101” → `P-101`
- select from constrained, read-only graph tools
- formulate graph queries
- explain retrieved graph facts and evidence

### The LLM may not

- invent connectivity
- create unsupported graph edges
- override deterministic topology facts silently
- suppress uncertainty
- actuate plant equipment
- approve LOTO or operational safety actions
- make autonomous plant-control decisions

**Architectural rule:** the LLM explains retrieved truth; it does not manufacture it.

---

## Flagship MVP

The first demonstrable product is intentionally narrow:

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

### Golden demo question

> **“What is downstream of P-101?”**

HRIDAY should be able to return a graph path such as:

```text
P-101 → E-101 → V-102
```

and show the engineer **where the evidence came from**.

A deliberately ambiguous drawing should instead trigger:

```text
Confidence: 0.62
Human verification required.
```

That behavior is a feature, not a failure.

---

## Architecture

```text
frontend/
   │
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
   ├── Query
   ├── Evidence
   └── Verification
```

The internal flow is contract-driven:

```text
DocumentInput
      ↓
ExtractionResult
      ↓
TopologyResult
      ↓
GraphResult
      ↓
QueryResult
      ↓
Evidence-backed Answer
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) and the detailed domain docs in [`docs/architecture/`](docs/architecture/).

---

## Repository philosophy

This repository is deliberately structured so **six people — including AI coding agents — can work in parallel without turning the project into merge-conflict soup.**

### Contracts are the constitution

`contracts/` defines what subsystems exchange.

If Member A changes how extraction works internally, Member B should still receive the same `ExtractionResult` contract.

If the graph backend changes from NetworkX to Neo4j, the query layer should not care.

### Ownership is explicit

Each contributor owns a bounded part of the tree. Do not “fix” another subsystem by editing it directly. Coordinate through interfaces, issues, or PRs.

### Prototype first, infrastructure second

The default prototype graph backend is expected to be an in-process implementation (e.g. NetworkX) behind `GraphStore`. Neo4j is an adapter target, not a reason to block the MVP.

---

## Intended stack

| Layer | Direction |
|---|---|
| Frontend | Next.js + TypeScript |
| API | Python + FastAPI |
| Vision / geometry | OpenCV + selected local CV tools |
| OCR | Pluggable OCR adapter |
| Multimodal reasoning | Open-weight local VLM, benchmark-selected |
| Graph | `GraphStore` abstraction; NetworkX first, Neo4j-compatible |
| Agent | Local model + constrained tools |
| Data contracts | JSON Schema |
| Tests | Pytest + frontend test tooling |
| Deployment | Local / on-premise |

Nothing in this table is a promise that every listed technology is mandatory. Interfaces should remain replaceable.

---

## Safety boundary

HRIDAY is a **read-only engineering intelligence and verification workbench** for the MVP.

It is not:

- a plant control system
- an autonomous operations system
- a LOTO approval system
- a safety interlock
- a substitute for engineering judgment

Any future safety-sensitive use must introduce an explicit authorization and validation architecture beyond this prototype.

---

## Research foundation

The architecture builds on research across several stages of engineering-diagram intelligence:

- **Mani et al. (CVPRW 2020)** — engineering diagram digitization using deep learning and graph search.
- **Paliwal et al. (PAKDD 2021)** — P&ID digitization with domain-guided validation and correction.
- **Bai et al. (CVPR 2026)** — end-to-end hyper-relational engineering-diagram extraction.
- **Zhu et al. (2026)** — multimodal P&ID extraction followed by explicit process-topology reconstruction.
- **Alimin & Schweidtmann (2026)** — GraphRAG-based interaction with P&IDs.

HRIDAY's engineering direction is to integrate these ideas into a sovereign workflow where graph facts retain visual evidence and uncertain interpretations can be reviewed by a human.

Research notes live in [`docs/research/`](docs/research/).

---

## Evaluation philosophy

All performance claims in this repository must be labeled as one of:

- **Target** — intended benchmark objective, not yet measured.
- **Measured** — obtained from a defined experiment with reproducible methodology.
- **Paper result** — reported by an external research paper, not by HRIDAY.

Never present another paper's accuracy as HRIDAY's accuracy.

The evaluation plan lives in [`docs/evaluation/METRICS.md`](docs/evaluation/METRICS.md).

---

## Development rules

### Never

```text
❌ push directly to main
❌ force-push shared branches
❌ reset or clean another developer's work
❌ silently change a contract
❌ invent graph facts
❌ commit secrets or .env files
❌ add random dependencies because a code generator suggested them
❌ refactor unrelated modules while implementing a feature
```

### Always

```text
✅ work on a feature branch
✅ respect folder ownership
✅ read AGENTS.md before using an AI coding agent
✅ read ARCHITECTURE.md before changing architecture
✅ read your role document before coding
✅ add tests for non-trivial logic
✅ inspect git diff before committing
✅ make uncertainty explicit
```

---

## Development through September 8

The prototype is optimized around one convincing vertical slice rather than breadth:

```text
Day 1  → contracts + repository foundation
Day 2  → extraction fixtures + real extraction path
Day 3  → topology reconstruction
Day 4  → graph + deterministic traversal
Day 5  → natural-language query + constrained agent
Day 6  → evidence + HITL
Day 7  → integration + demo polish
Day 8  → freeze, test, rehearse
```

The team may change implementation details while preserving the architectural contracts and safety boundary.

---

## Suggested demo scenarios

### Simple chain

```text
V-101 → P-101 → E-101 → V-102
```

### Branching process

```text
             → V-102
            /
P-101 → E-101
            \
             → V-103
```

### Ambiguous crossing

Use a deliberately ambiguous crossing/junction so the system can demonstrate **“I don't know yet — please verify”** rather than hallucinating an edge.

---

## Project status

**Stage:** architecture + repository bootstrap

**Current priority:** make the end-to-end contract-driven demo work with controlled fixtures, then progressively replace mocked stages with real implementations.

**Do not confuse this repository's targets, research results, or planned components with measured HRIDAY performance.**

---

## Team

**GARUD** is the team name.

**HRIDAY** is the project.

Member assignments are intentionally left open until the team meeting so contributors can choose roles according to capability.

Prepared role packages live under [`docs/development/`](docs/development/).

---

## License

Choose the project's final license deliberately after confirming SIH rules, third-party model/tool licenses, and the team's preferred reuse policy. Until then, treat this repository as project source code rather than making an unsupported licensing claim.

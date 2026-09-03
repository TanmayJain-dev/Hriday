# Role Packages

Member numbers are assigned by the team. These packages describe the work; names are intentionally left open until the team meeting.

## Role 1 — Core Architecture & Graph Intelligence

Hardest technical package.

Own:
- contracts
- pipeline orchestration
- graph ontology
- `GraphStore` interface
- NetworkX implementation
- traversal semantics
- graph validation hooks
- query intent semantics
- provenance propagation
- confidence propagation
- integration tests

Success criterion: every answer can be reproduced from deterministic graph operations and linked evidence.

## Role 2 — Frontend & Visualization

Own upload, processing state, P&ID viewer, graph visualization, query UI, evidence highlighting, and verification UI.

## Role 3 — Visual Extraction

Own image/PDF preprocessing, OCR adapter, detector adapter, text/entity association, line candidates, and extraction confidence.

## Role 4 — Topology Reconstruction

Own line tracing, endpoints, junction-vs-crossing decisions, geometry, object-line association, topology confidence, and topology rules.

## Role 5 — Agent Integration

Own entity resolution, intent parsing, constrained tool definitions, local-model adapter, query planning, and explanation assembly.

The agent never mutates topology directly.

## Role 6 — Evidence & Human Verification

Own evidence mapping, confidence reporting, review queue, confirm/reject/edit decisions, graph correction events, and review contracts.

# Role Packages

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

Primary success criterion: every answer can be reproduced from deterministic graph operations and linked evidence.

## Role 2 — Frontend & Visualization

Own:
- upload experience
- processing state
- P&ID viewer
- graph visualization
- query UI
- evidence highlighting
- verification interface

## Role 3 — Visual Extraction

Own:
- image/PDF preprocessing
- OCR adapter
- detector adapter
- text/entity association
- line candidates
- extraction confidence

## Role 4 — Topology Reconstruction

Own:
- line tracing
- endpoint detection
- junction vs crossing analysis
- connection inference
- geometric validation
- topology confidence

## Role 5 — Agent & Tool Integration

Own:
- entity resolution
- intent handling
- constrained graph tools
- local model adapter
- answer explanation

The agent consumes graph truth; it does not invent topology.

## Role 6 — Evidence & Human Verification

Own:
- evidence mapping
- confidence gate presentation
- review queue
- confirm/reject/edit decisions
- correction events
- provenance history

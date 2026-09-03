# HRIDAY Architecture

## 1. System objective

HRIDAY turns a supported P&ID drawing into a queryable, provenance-aware engineering graph.

```text
Document
  ↓
Observation
  ↓
Interpretation
  ↓
Topology
  ↓
Graph Fact
  ↓
Query
  ↓
Evidence-backed Answer
  ↓
Human Verification when required
```

## 2. Truth hierarchy

```text
1. Visual evidence
2. Deterministic geometric observations
3. Domain validation rules
4. Reconstructed topology
5. Persisted graph facts
6. Retrieved graph result
7. LLM explanation
```

Never reverse this hierarchy.

## 3. Pipeline stages

### Ingestion
Normalizes a PDF/image/scan into a document representation without destroying page identity or source coordinates.

### Extraction
Produces observable entities, text regions, coordinates, line candidates and uncertainty.

### Topology
Determines supported connections from geometry, junctions, endpoints, arrows and domain rules.

### Graph
Persists entities and relationships with provenance and confidence.

### Query
Maps user intent to constrained graph operations.

### Evidence
Maps graph claims back to source regions and confidence signals.

### Verification
Routes uncertain claims to a human and records confirm/reject/edit decisions.

## 4. Component boundaries

```text
ExtractionResult → TopologyEngine
TopologyResult   → GraphBuilder
GraphStore       → QueryEngine
QueryResult      → AnswerAssembler
EvidenceStore    → AnswerAssembler
Verification     → Graph correction event
```

## 5. GraphStore abstraction

The rest of the system must not import NetworkX or Neo4j directly.

```text
GraphStore
├── NetworkXGraphStore
└── Neo4jGraphStore
```

The MVP should prefer the simplest reliable in-process implementation.

## 6. Agent boundary

Agent loop:

```text
question
 ↓
intent resolution
 ↓
entity resolution
 ↓
constrained tool selection
 ↓
GraphStore operation
 ↓
retrieved facts
 ↓
evidence lookup
 ↓
confidence gate
 ↓
explanation
```

The agent does not directly mutate graph topology.

## 7. Failure principle

When the system does not know, the system must say that it does not know.

Examples:

- ambiguous crossing → review
- missing tag → unresolved entity
- unsupported symbol → unsupported extraction
- weak evidence → low-confidence answer
- unavailable model → explicit processing failure

## 8. MVP scope

Supported cases are intentionally limited. Extensibility matters more than pretending to solve every industrial drawing style.

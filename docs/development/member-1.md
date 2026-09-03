# Member 1 — Core Architecture & Graph Intelligence

This is the deepest technical role in the prototype. The assigned person owns the engineering core, not everyone else's code.

## Primary ownership

- `contracts/`
- `backend/orchestration/`
- `backend/intelligence/graph/`
- graph/query semantics
- integration tests

## Hard technical backlog

1. Define the canonical engineering graph model.
2. Implement the `GraphStore` interface.
3. Implement an in-process graph backend first.
4. Implement upstream/downstream/path traversal.
5. Build graph construction from `TopologyResult`.
6. Preserve evidence and confidence through graph facts.
7. Define supported query intents.
8. Implement query planning over constrained graph operations.
9. Add graph validation hooks.
10. Integrate the vertical pipeline.
11. Own cross-subsystem integration tests.

## Invariants

- unsupported edges are never silently accepted
- every returned claim can expose its graph path
- graph claims can request source evidence
- uncertainty survives the pipeline
- the LLM cannot directly mutate topology

## Important boundary

Do not become the project's universal fixer. When another subsystem is wrong, prefer a contract-level change, issue, or review request over editing its internals.

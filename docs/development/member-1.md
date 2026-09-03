# Member 1 — Core Architecture & Graph Intelligence

## Mission

Own the technical center of HRIDAY. Build the contracts, graph abstraction, deterministic graph behavior, pipeline orchestration and integration layer that allow every other subsystem to plug together cleanly.

## Owned paths

- `contracts/**`
- `backend/orchestration/**`
- `backend/intelligence/graph/**`
- `backend/intelligence/query/**` when it concerns graph semantics/tool contracts
- `backend/api/**` only for integration wiring
- `tests/graph/**`
- `tests/query/**`
- `tests/integration/**`
- architecture decision records

## Do not casually edit

- `frontend/**`
- `backend/intelligence/extraction/**`
- `backend/intelligence/topology/**`
- `backend/evidence/**`
- `backend/verification/**`

## Hard deliverables

1. Canonical graph model.
2. `GraphStore` interface.
3. In-process NetworkX implementation.
4. Graph builder from `TopologyResult`.
5. Deterministic downstream/upstream/path operations.
6. Provenance + confidence propagation.
7. Query intent schema and read-only graph tool boundary.
8. Pipeline orchestration.
9. End-to-end integration tests using fixtures.

## Engineering standard

Never solve a graph problem by asking the LLM to guess. The LLM may plan a constrained query; the graph engine decides the result.

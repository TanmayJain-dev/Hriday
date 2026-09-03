# ADR-002 — Graph Store Abstraction

## Decision

Use a `GraphStore` interface and allow an in-process graph implementation for the MVP, with a Neo4j adapter target.

## Why

The prototype deadline is short. Graph semantics, provenance and querying matter more than database infrastructure.

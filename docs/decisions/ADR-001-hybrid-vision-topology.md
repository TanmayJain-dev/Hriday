# ADR-001 — Hybrid Visual Extraction and Deterministic Topology

## Decision

Separate multimodal perception from topology reconstruction.

## Why

Dense engineering drawings contain thin geometry, ambiguous crossings, and relationships that are poorly represented by text-only similarity. The architecture therefore uses visual models for observation and deterministic geometry/rules for connectivity wherever feasible.

## Consequence

The system becomes more modular and auditable, but implementation is more involved than a single VLM call.

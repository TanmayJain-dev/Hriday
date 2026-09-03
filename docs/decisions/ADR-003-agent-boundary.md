# ADR-003 — Constrained Agent Boundary

## Decision

The local LLM can plan and explain read-only graph operations, but cannot directly invent or mutate topology.

## Why

The system must remain evidence-backed and auditable.

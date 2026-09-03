# AI Agent Guide

This repository is designed to be usable by coding agents with no additional project prompt.

## First reads

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `docs/development/ROLE_PACKAGES.md`
4. your `docs/development/member-X.md`
5. the relevant files under `contracts/`

## Work pattern

Understand the contract first. Inspect neighboring code. Make the smallest change. Add tests. Validate. Inspect the diff. Never compensate for another subsystem by rewriting it.

## If blocked

Report the missing interface, fixture, dependency or decision instead of inventing a new architecture.

## Most important invariant

If a claim about connectivity cannot be grounded in visual evidence, deterministic geometry/rules, or a reviewed graph fact, the agent must not manufacture it.

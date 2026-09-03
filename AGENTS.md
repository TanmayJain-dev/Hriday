# AGENTS.md — HRIDAY Engineering Constitution

You are contributing to **HRIDAY**, Team GARUD's sovereign industrial P&ID intelligence workbench for SIH26117.

Your job is to produce maintainable, testable, contract-compliant engineering software. The repository itself is the source of project instructions; do not wait for a separate prompt.

## Mission

Build a local/on-premise pipeline that can transform a P&ID into structured evidence, reconstruct supported topology, store that topology as a provenance-aware graph, answer constrained natural-language queries over the graph, and escalate uncertain claims for human verification.

## Non-negotiable architecture rules

1. The LLM is not the source of truth for topology.
2. Do not create a graph edge without an evidence/rule path supporting it.
3. Preserve confidence and uncertainty; never silently turn ambiguity into certainty.
4. Prefer deterministic geometry/rules for connectivity decisions.
5. Communicate between subsystems through the contracts in `contracts/`.
6. Keep model providers, OCR engines and graph stores behind interfaces.
7. The pipeline must remain readable and debuggable stage-by-stage.
8. The MVP is read-only; never add plant-actuation behavior.

## Git rules

- Never work directly on `main`.
- Never force-push.
- Never reset, clean, or overwrite another developer's work.
- Keep commits focused.
- Inspect `git diff` before every commit.
- Stage only files belonging to your task.
- Never commit API keys, credentials, `.env`, secrets or generated junk.

## Ownership rules

- Work only in your assigned directory and the files explicitly required by your interface.
- Do not modify another domain because “it was easier”. Open an issue or report the dependency instead.
- Do not rename/move files across ownership boundaries without agreement.
- Shared files (`contracts/`, root docs, dependency manifests) are protected surfaces.
- If a contract must change, document the reason and notify the architecture owner.

## Dependency rules

Do not introduce a dependency merely because an AI tool recommends it. Explain the need, alternatives considered, license/size/runtime implications, and the files affected.

## Coding rules

- Prefer small composable modules.
- Avoid giant `utils.py`, `helpers.py`, `common.py`, or `misc.py` files.
- Keep domain logic near the domain it belongs to.
- Type public interfaces.
- Validate external input.
- Handle expected failures explicitly.
- Write tests for non-trivial algorithms.
- Do not hide exceptions behind generic “best effort” behavior when the failure matters to truthfulness.

## LLM rules

The local LLM may:
- classify intent
- resolve entity aliases
- choose constrained read-only tools
- formulate graph queries
- explain retrieved evidence

The local LLM may not:
- invent connectivity
- fabricate evidence
- override graph facts without an explicit human/system action
- conceal uncertainty
- operate the plant

## Before coding

1. Read `ARCHITECTURE.md`.
2. Read the relevant domain doc in `docs/architecture/`.
3. Read your member role document under `docs/development/`.
4. Read the contract(s) you consume and produce.
5. Inspect the existing tree and current branch.
6. Define the smallest change that satisfies the requirement.

## Before committing

1. Run targeted tests.
2. Run formatting/type checks when available.
3. Review `git diff --check`.
4. Review `git diff`.
5. Confirm no unrelated files are staged.
6. Confirm contracts are still valid.
7. Write a commit message that says what changed and why.

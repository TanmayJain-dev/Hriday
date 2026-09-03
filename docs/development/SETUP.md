# Local Setup

## Prerequisites

- Git
- Python 3.11+
- Node.js 20+ for the frontend

## Backend smoke test

```bash
python -m compileall backend
python scripts/validate_contracts.py
python scripts/run_demo.py
```

## Frontend

The frontend directory is intentionally a clean shell until the assigned frontend owner establishes the implementation and dependency policy.

## Local model

A provider adapter should point to a locally hosted open-weight model. Do not bake a specific vendor/API into domain logic.

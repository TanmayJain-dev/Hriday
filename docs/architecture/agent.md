# Agent Architecture

The agent is a constrained translator between human intent and deterministic graph operations.

```text
question
  ↓
intent resolution
  ↓
entity resolution
  ↓
read-only tool selection
  ↓
GraphStore
  ↓
retrieved facts
  ↓
evidence lookup
  ↓
confidence gate
  ↓
explanation
```

The model never gets authority to invent topology or mutate plant state.

# Query Architecture

Natural language is translated into constrained operations.

Example:

```text
"What is downstream of P-101?"
        ↓
intent = DOWNSTREAM
entity = P-101
        ↓
GraphStore.downstream(P-101)
```

The answer generator may explain only what the graph query actually returned.

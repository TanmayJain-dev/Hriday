# HRIDAY Architecture Overview

HRIDAY is a contract-driven, read-only pipeline for turning supported P&ID drawings into provenance-aware engineering graphs and evidence-backed answers.

```text
P&ID → observation → topology → graph fact → query → evidence-backed answer → verification
```

Core invariant: the system must be able to explain why a claimed relationship exists.

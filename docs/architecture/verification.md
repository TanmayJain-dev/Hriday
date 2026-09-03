# Verification Architecture

Confidence should be treated as an explicit state machine, not a decorative number.

```text
AUTO_GENERATED
      ↓
confidence gate
      ↓
┌───────────────┐
│               │
HIGH            LOW
│               │
▼               ▼
ANSWER      REVIEW_REQUIRED
                ↓
          CONFIRM / REJECT / EDIT
                ↓
            NEW GRAPH STATE
```

Thresholds should be configurable and benchmarked rather than embedded as undocumented magic numbers.

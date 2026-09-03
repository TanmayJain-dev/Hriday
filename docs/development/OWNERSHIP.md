# Ownership Boundaries

Member identities are assigned by the team. These are role boundaries, not permanent personal assignments.

| Role | Primary ownership | Protected surfaces |
|---|---|---|
| Core Architecture & Graph Intelligence | `contracts/`, `backend/orchestration/`, `backend/intelligence/graph/`, core query semantics | all other domains except through contracts/review |
| Frontend & Visualization | `frontend/` | backend internals |
| Visual Extraction | `backend/intelligence/extraction/`, extraction tests/docs | topology/graph/query internals |
| Topology Reconstruction | `backend/intelligence/topology/`, topology tests/docs | extraction/graph/query internals |
| Agent Integration | `backend/intelligence/query/` agent/tooling | topology internals |
| Evidence & Verification | `backend/evidence/`, `backend/verification/` | graph algorithms/frontend |

Cross-domain changes require a PR note explaining the dependency.

Shared files such as `contracts/`, root architecture documents, dependency manifests, and CI configuration are protected surfaces. Coordinate before changing them.

# Member 5 — Agent & Tool Integration

Own the agent-facing portion of `backend/intelligence/query/**` and related tests, without changing graph semantics owned by Member 1.

Mission: map natural-language questions to constrained, read-only graph operations and explain only retrieved facts.

Build entity resolution, intent handling, tool wrappers, local model adapter, and response assembly hooks.

Do not let the model directly mutate graph topology or invent unsupported relationships.

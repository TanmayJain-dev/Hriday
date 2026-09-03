# Security Boundary

HRIDAY is designed for sensitive industrial engineering material.

## MVP security posture

- Local/on-premise execution is the target deployment model.
- External AI APIs are not required by the architectural contract.
- Do not log raw P&ID images, full document text, secrets, credentials or sensitive engineering content unnecessarily.
- Keep temporary files under controlled local storage.
- Do not commit real industrial documents to the repository.
- Use synthetic or sanitized fixtures in `data/`.
- Keep model/provider credentials out of source control.
- The MVP is read-only with respect to industrial systems.

This is a prototype security posture, not a production security certification.

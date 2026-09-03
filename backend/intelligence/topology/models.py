from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class TopologyNode:
    id: str
    type: str
    confidence: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TopologyEdge:
    source: str
    target: str
    relationship: str = "CONNECTED_TO"
    confidence: float = 1.0
    evidence_ids: tuple[str, ...] = ()
    requires_verification: bool = False

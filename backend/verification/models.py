from dataclasses import dataclass
from typing import Literal

VerificationStatus = Literal["not_required", "pending", "confirmed", "rejected", "corrected"]

@dataclass(frozen=True)
class VerificationDecision:
    status: VerificationStatus
    review_id: str | None = None
    comment: str | None = None

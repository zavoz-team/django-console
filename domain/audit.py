from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class AuditEntry:
    id: int
    actor_email: str
    action: str
    target_type: str
    target_id: str
    status: str
    payload_json: Mapping[str, str | int | float | bool]
    trace_id: str | None = None
    created_at: datetime | None = None

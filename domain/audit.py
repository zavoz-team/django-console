from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class AuditEntry:
    id: str
    at: datetime
    actor: str
    action: str
    target_type: str | None = None
    target_id: str | None = None
    fields: Mapping[str, str] | None = None

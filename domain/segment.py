from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentSummary:
    id: str
    name: str
    members_count: int | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentMember:
    segment_id: str
    profile_id: str
    added_at: datetime | None = None

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentSummary:
    segment_id: str
    name: str
    description: str
    is_active: bool
    members_count: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentMember:
    segment_id: str
    customer_id: str
    email: str | None = None
    phone: str | None = None
    external_user_id: str | None = None

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UiErrorViewModel:
    message: str


@dataclass(frozen=True, slots=True)
class DetailItemViewModel:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class ProfileRowViewModel:
    customer_id: str
    email: str
    phone: str
    last_seen_at: str
    external_user_id: str | None
    segments: list[str]
    total_orders: int
    total_revenue: float


@dataclass(frozen=True, slots=True)
class ProfileDetailViewModel:
    customer_id: str
    emails: list[str]
    phones: list[str]
    attributes: dict
    total_revenue: float
    currency: str | None
    last_seen_at: str | None
    segments: list[str]


@dataclass(frozen=True, slots=True)
class SegmentRowViewModel:
    segment_id: str
    name: str
    description: str
    is_active: bool
    members_count: str


@dataclass(frozen=True, slots=True)
class SegmentMemberViewModel:
    customer_id: str
    segment_id: str
    email: str | None
    phone: str | None


@dataclass(frozen=True, slots=True)
class JobRowViewModel:
    job_id: str
    segment_id: str
    status: str
    requested_at: str
    completed_at: str
    members_count: str
    error_reason: str
    requested_by: str | None


@dataclass(frozen=True, slots=True)
class AuditEntryViewModel:
    id: int
    actor_email: str
    action: str
    target_type: str
    target_id: str
    status: str
    created_at: str

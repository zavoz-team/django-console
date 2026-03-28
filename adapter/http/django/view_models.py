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
    id: str
    display_name: str
    email: str
    phone: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ProfileDetailViewModel:
    id: str
    display_name: str
    email: str
    phone: str
    updated_at: str
    attributes: list[DetailItemViewModel]


@dataclass(frozen=True, slots=True)
class SegmentRowViewModel:
    id: str
    name: str
    members_count: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class SegmentMemberViewModel:
    segment_id: str
    profile_id: str
    added_at: str


@dataclass(frozen=True, slots=True)
class JobRowViewModel:
    id: str
    status: str
    created_at: str
    finished_at: str
    records_count: str
    error_code: str


@dataclass(frozen=True, slots=True)
class AuditEntryViewModel:
    id: int
    actor_email: str
    action: str
    target_type: str
    target_id: str
    status: str
    created_at: str

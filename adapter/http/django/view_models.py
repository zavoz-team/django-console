from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UiErrorViewModel:
    message: str


@dataclass(frozen=True, slots=True)
class DetailItemViewModel:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class AuditEntryViewModel:
    id: int
    actor_email: str
    action: str
    target_type: str
    target_id: str
    status: str
    created_at: str

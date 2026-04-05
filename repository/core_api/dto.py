from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CoreApiProfileDTO:
    id: str
    email: str
    name: str
    created_at: str
    updated_at: str
    status: str
    custom_fields: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CoreApiSegmentDTO:
    id: str
    name: str
    status: str
    created_at: str


@dataclass(frozen=True, slots=True)
class CoreApiExportJobDTO:
    id: str
    segment_id: str
    status: str
    created_at: str
    updated_at: str
    completed_at: str | None

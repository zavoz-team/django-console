from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileSummary:
    id: str
    display_name: str
    email: str | None = None
    phone: str | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileDetails:
    id: str
    display_name: str
    email: str | None = None
    phone: str | None = None
    updated_at: datetime | None = None
    attributes: Mapping[str, str] | None = None

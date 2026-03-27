from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class CoreApiProfileDTO:
    id: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CoreApiSegmentDTO:
    id: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CoreApiJobDTO:
    id: str
    status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CoreApiSystemStatusDTO:
    status: str

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileDTO:
    id: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentDTO:
    id: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class JobDTO:
    id: str
    status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SystemStatusDTO:
    status: str

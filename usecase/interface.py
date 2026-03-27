from collections.abc import Mapping, Sequence
from types import TracebackType
from typing import Protocol, TypeAlias

from domain.audit import AuditEntry
from domain.export_job import ExportJobSummary
from domain.profile import ProfileDetails, ProfileSummary
from domain.query import Pagination, TextQuery
from domain.segment import SegmentMember, SegmentSummary
from domain.user import User
from usecase.dto import JobDTO, ProfileDTO, SegmentDTO, SystemStatusDTO

AttrValue: TypeAlias = str | int | float | bool
Attrs: TypeAlias = Mapping[str, AttrValue]


class UserRepository(Protocol):
    def get(self, user_id: str) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def save(self, user: User) -> None: ...


class ProfileGateway(Protocol):
    def get(self, profile_id: str) -> ProfileDetails | None: ...

    def list(
        self,
        pagination: Pagination,
        query: TextQuery | None = None,
    ) -> list[ProfileSummary]: ...


class SegmentGateway(Protocol):
    def list_segments(self, pagination: Pagination) -> list[SegmentSummary]: ...

    def list_members(
        self,
        segment_id: str,
        pagination: Pagination,
    ) -> list[SegmentMember] | None: ...


class ExportGateway(Protocol):
    def trigger(
        self,
        segment_id: str,
        destination: str,
    ) -> ExportJobSummary: ...

    def list_jobs(self, pagination: Pagination) -> list[ExportJobSummary]: ...


class SystemGateway(Protocol):
    def is_core_available(self) -> bool: ...


class AuditLogRepository(Protocol):
    def save(self, entry: AuditEntry) -> AuditEntry: ...

    def list_recent(self, pagination: Pagination) -> list[AuditEntry]: ...

    def list_by_target(
        self,
        target_type: str,
        target_id: str,
        pagination: Pagination,
    ) -> list[AuditEntry]: ...


class Logger(Protocol):
    def debug(self, message: str, attrs: Attrs | None = None) -> None: ...

    def info(self, message: str, attrs: Attrs | None = None) -> None: ...

    def warning(self, message: str, attrs: Attrs | None = None) -> None: ...

    def error(self, message: str, attrs: Attrs | None = None) -> None: ...


class Metrics(Protocol):
    def increment(
        self,
        name: str,
        value: int = 1,
        attrs: Attrs | None = None,
    ) -> None: ...

    def record(
        self,
        name: str,
        value: float,
        attrs: Attrs | None = None,
    ) -> None: ...


class Span(Protocol):
    def set_attribute(self, name: str, value: AttrValue) -> None: ...

    def record_error(self, error: Exception) -> None: ...


class SpanContext(Protocol):
    def __enter__(self) -> Span: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...


class Tracer(Protocol):
    def start_span(
        self,
        name: str,
        attrs: Attrs | None = None,
    ) -> SpanContext: ...


class ProfileGateway(Protocol):
    def list_profiles(self, limit: int = 50, offset: int = 0) -> Sequence[ProfileDTO]: ...

    def get_profile(self, customer_id: str) -> ProfileDTO | None: ...


class SegmentGateway(Protocol):
    def list_segments(self, limit: int = 50, offset: int = 0) -> Sequence[SegmentDTO]: ...

    def get_segment_members(self, segment_id: str, limit: int = 50, offset: int = 0) -> Sequence[ProfileDTO]: ...


class ExportGateway(Protocol):
    def trigger_export(self, segment_id: str) -> str: ...


class JobGateway(Protocol):
    def list_jobs(self, limit: int = 50, offset: int = 0) -> Sequence[JobDTO]: ...

    def get_job(self, job_id: str) -> JobDTO | None: ...


class SystemStatusGateway(Protocol):
    def get_status(self) -> SystemStatusDTO: ...


class AuditGateway(Protocol):
    def log_action(self, operator_id: str, action: str, target_id: str | None = None) -> None: ...

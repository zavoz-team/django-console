from collections.abc import Mapping, Sequence
from types import TracebackType
from typing import Any, Optional, Protocol, TypeAlias

from domain.audit import AuditEntry
from domain.export_job import ExportJob
from domain.profile import Profile
from domain.query import Pagination, TextQuery
from domain.segment import Segment
from domain.user import User


AttrValue: TypeAlias = str | int | float | bool
Attrs: TypeAlias = Mapping[str, AttrValue]


class CoreApiClientInterface(Protocol):
    def shutdown(self) -> None: ...

    def get_profiles(
        self,
        limit: int,
        offset: int,
        query: TextQuery | None = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> list[dict[str, Any]]: ...

    def get_profile(
        self, customer_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]: ...

    def get_segments(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> list[dict[str, Any]]: ...

    def get_segment_members(
        self,
        segment_id: str,
        limit: int,
        offset: int,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> list[dict[str, Any]]: ...

    def trigger_export(
        self, segment_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]: ...

    def get_jobs(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> list[dict[str, Any]]: ...

    def get_job(
        self, job_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]: ...

    def get_system_status(
        self, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]: ...

    def log_audit_action(
        self, payload: dict[str, Any], extra_headers: Optional[dict[str, str]] = None
    ) -> None: ...


class UserRepository(Protocol):
    def get(self, user_id: str) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def save(self, user: User) -> None: ...


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
    def list_profiles(
        self, pagination: Pagination, query: TextQuery | None = None
    ) -> Sequence[Profile]: ...

    def get_profile(self, customer_id: str) -> Profile | None: ...


class SegmentGateway(Protocol):
    def list_segments(
        self, limit: int = 50, offset: int = 0
    ) -> Sequence[Segment]: ...

    def get_segment_members(
        self, segment_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[Profile]: ...


class ExportGateway(Protocol):
    def trigger_export(
        self, segment_id: str, actor_id: str, trace_id: str
    ) -> ExportJob: ...

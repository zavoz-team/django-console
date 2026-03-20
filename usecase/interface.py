from collections.abc import Mapping
from types import TracebackType
from typing import Protocol, TypeAlias

from domain.user import User

AttrValue: TypeAlias = str | int | float | bool
Attrs: TypeAlias = Mapping[str, AttrValue]


class UserRepository(Protocol):
    def get(self, user_id: str) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def save(self, user: User) -> None: ...


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

from collections.abc import Mapping

from django.http import HttpRequest

from domain.audit import AuditEntry
from domain.query import Pagination


def read_text(request: HttpRequest, name: str) -> str | None:
    value = request.GET.get(name)
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def read_pagination(
    request: HttpRequest,
    *,
    default_limit: int = 20,
) -> Pagination:
    raw_limit = request.GET.get('limit')
    raw_offset = request.GET.get('offset')
    limit = default_limit if raw_limit is None else int(raw_limit)
    offset = 0 if raw_offset is None else int(raw_offset)
    return Pagination(limit=limit, offset=offset)


def unavailable_context(
    *,
    title: str,
    message: str,
    values: Mapping[str, str],
) -> dict[str, object]:
    return {
        'title': title,
        'message': message,
        'values': values,
    }


def audit_context(
    *,
    entries: list[AuditEntry],
    limit: int,
    offset: int,
    error: str | None = None,
) -> dict[str, object]:
    return {
        'title': 'Audit',
        'entries': entries,
        'limit': limit,
        'offset': offset,
        'error': error,
    }

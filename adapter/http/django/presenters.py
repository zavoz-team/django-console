from collections.abc import Mapping
from datetime import datetime

from django.forms import BaseForm

from domain.audit import AuditEntry
from domain.query import Pagination
from adapter.http.django.view_models import (
    AuditEntryViewModel,
    DetailItemViewModel,
    UiErrorViewModel,
)


def read_pagination(
    form: object,
    *,
    default_limit: int = 20,
) -> Pagination:
    cleaned_data = getattr(form, 'cleaned_data', {})
    limit = cleaned_data.get('limit') or default_limit
    offset = cleaned_data.get('offset') or 0
    return Pagination(limit=limit, offset=offset)


def ui_errors(
    form: BaseForm | None = None,
    *,
    messages: tuple[str, ...] = (),
) -> list[UiErrorViewModel]:
    items = [UiErrorViewModel(message=message) for message in messages]
    if form is None or not form.is_bound or form.is_valid():
        return items

    for error in form.non_field_errors():
        items.append(UiErrorViewModel(message=str(error)))

    for field in form:
        for error in field.errors:
            items.append(UiErrorViewModel(message=f'{field.label}: {error}'))
    return items


def detail_items(values: Mapping[str, str] | None = None) -> list[DetailItemViewModel]:
    if values is None:
        return []
    return [
        DetailItemViewModel(label=label, value=value)
        for label, value in values.items()
    ]


def ui_context(
    *,
    title: str,
    message: str | None = None,
    errors: list[UiErrorViewModel] | None = None,
    values: Mapping[str, str] | None = None,
    form: object | None = None,
    forms: Mapping[str, object] | None = None,
) -> dict[str, object]:
    context: dict[str, object] = {'title': title}
    if message is not None:
        context['message'] = message
    context['ui_errors'] = [] if errors is None else errors
    context['details'] = detail_items(values)
    if form is not None:
        context['form'] = form
    if forms is not None:
        context['forms'] = forms
    return context


def audit_context(
    *,
    entries: list[AuditEntry],
    limit: int,
    offset: int,
    errors: list[UiErrorViewModel] | None = None,
) -> dict[str, object]:
    rows = [audit_row(entry) for entry in entries]
    context: dict[str, object] = {
        'title': 'Audit',
        'entries': rows,
        'limit': limit,
        'offset': offset,
        'ui_errors': [] if errors is None else errors,
    }
    return context


def audit_row(entry: AuditEntry) -> AuditEntryViewModel:
    return AuditEntryViewModel(
        id=entry.id,
        actor_email=entry.actor_email,
        action=entry.action,
        target_type=entry.target_type,
        target_id=entry.target_id,
        status=entry.status,
        created_at=_format_datetime(entry.created_at),
    )


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return ''
    return value.isoformat()

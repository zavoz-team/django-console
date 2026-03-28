from collections.abc import Mapping
from datetime import datetime

from django.forms import BaseForm

from domain.audit import AuditEntry
from domain.export_job import ExportJobSummary
from domain.profile import ProfileDetails, ProfileSummary
from domain.segment import SegmentMember, SegmentSummary
from adapter.http.django.view_models import (
    AuditEntryViewModel,
    DetailItemViewModel,
    JobRowViewModel,
    ProfileDetailViewModel,
    ProfileRowViewModel,
    SegmentMemberViewModel,
    SegmentRowViewModel,
    UiErrorViewModel,
)


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


def profile_rows(items: list[ProfileSummary]) -> list[ProfileRowViewModel]:
    return [
        ProfileRowViewModel(
            id=item.id,
            display_name=item.display_name,
            email=item.email or '',
            phone=item.phone or '',
            updated_at=_format_datetime(item.updated_at),
        )
        for item in items
    ]


def profile_detail(item: ProfileDetails) -> ProfileDetailViewModel:
    attributes = item.attributes or {}
    return ProfileDetailViewModel(
        id=item.id,
        display_name=item.display_name,
        email=item.email or '',
        phone=item.phone or '',
        updated_at=_format_datetime(item.updated_at),
        attributes=detail_items(attributes),
    )


def segment_rows(items: list[SegmentSummary]) -> list[SegmentRowViewModel]:
    return [
        SegmentRowViewModel(
            id=item.id,
            name=item.name,
            members_count=_format_optional_int(item.members_count),
            updated_at=_format_datetime(item.updated_at),
        )
        for item in items
    ]


def segment_member_rows(
    items: list[SegmentMember],
) -> list[SegmentMemberViewModel]:
    return [
        SegmentMemberViewModel(
            segment_id=item.segment_id,
            profile_id=item.profile_id,
            added_at=_format_datetime(item.added_at),
        )
        for item in items
    ]


def job_rows(items: list[ExportJobSummary]) -> list[JobRowViewModel]:
    return [job_row(item) for item in items]


def job_row(item: ExportJobSummary) -> JobRowViewModel:
    return JobRowViewModel(
        id=item.id,
        status=_format_value(item.status),
        created_at=_format_datetime(item.created_at),
        finished_at=_format_datetime(item.finished_at),
        records_count=_format_optional_int(item.records_count),
        error_code=item.error_code or '',
    )


def ui_context(
    *,
    title: str,
    message: str | None = None,
    errors: list[UiErrorViewModel] | None = None,
    values: Mapping[str, str] | None = None,
    form: object | None = None,
    forms: Mapping[str, object] | None = None,
    extra: Mapping[str, object] | None = None,
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
    if extra is not None:
        context.update(extra)
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


def _format_optional_int(value: int | None) -> str:
    if value is None:
        return ''
    return str(value)


def _format_value(value: object) -> str:
    result = getattr(value, 'value', None)
    if isinstance(result, str):
        return result
    return str(value)

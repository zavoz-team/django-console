from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.forms import SegmentMembersFilterForm, SegmentsFilterForm
from adapter.http.django.presenters import (
    segment_member_rows,
    segment_rows,
    ui_context,
    ui_errors,
)
from adapter.http.django.runtime import get_container
from domain.error import CoreUnavailableError, SegmentNotFoundError
from usecase.segment import GetSegmentMembersQuery, ListSegmentsQuery


@login_required
@require_GET
def segments_page(request: HttpRequest) -> HttpResponse:
    form = SegmentsFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        context = ui_context(
            title='Segments',
            errors=ui_errors(form),
            form=form,
        )
        return render(request, 'backoffice/segments.html', context, status=400)

    try:
        segments = get_container().usecases.list_segments.execute(
            ListSegmentsQuery(pagination=form.pagination())
        )
    except CoreUnavailableError:
        context = ui_context(
            title='Segments',
            errors=ui_errors(messages=('unavailable',)),
            form=form,
        )
        return render(request, 'backoffice/segments.html', context, status=503)

    context = ui_context(
        title='Segments',
        form=form,
        extra={'rows': segment_rows(list(segments))},
    )
    return render(request, 'backoffice/segments.html', context)


@login_required
@require_GET
def segment_members_page(request: HttpRequest, segment_id: str) -> HttpResponse:
    form = SegmentMembersFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        context = ui_context(
            title='Segment Members',
            errors=ui_errors(form),
            form=form,
            values={'segment_id': segment_id},
        )
        return render(request, 'backoffice/segment_members.html', context, status=400)

    try:
        members = get_container().usecases.get_segment_members.execute(
            GetSegmentMembersQuery(
                segment_id=segment_id,
                pagination=form.pagination(),
            )
        )
    except SegmentNotFoundError:
        context = ui_context(
            title='Segment Members',
            errors=ui_errors(messages=('not found',)),
            form=form,
            values={'segment_id': segment_id},
        )
        return render(request, 'backoffice/segment_members.html', context, status=404)
    except CoreUnavailableError:
        context = ui_context(
            title='Segment Members',
            errors=ui_errors(messages=('unavailable',)),
            form=form,
            values={'segment_id': segment_id},
        )
        return render(request, 'backoffice/segment_members.html', context, status=503)

    context = ui_context(
        title='Segment Members',
        form=form,
        values={'segment_id': segment_id},
        extra={'rows': segment_member_rows(list(members))},
    )
    return render(request, 'backoffice/segment_members.html', context)

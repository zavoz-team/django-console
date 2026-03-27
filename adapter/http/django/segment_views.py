from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.forms import SegmentFilterForm, SegmentMembersFilterForm
from adapter.http.django.presenters import ui_context, ui_errors


def _render_unavailable(
    request: HttpRequest,
    *,
    title: str,
    form: object,
    status: int,
    errors: list | None = None,
    values: dict[str, str] | None = None,
) -> HttpResponse:
    context = ui_context(
        title=title,
        message='usecase wiring pending',
        errors=errors,
        values=values,
        form=form,
    )
    return render(request, 'backoffice/unavailable.html', context, status=status)


@login_required
@require_GET
def segments_page(request: HttpRequest) -> HttpResponse:
    form = SegmentFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        return _render_unavailable(
            request,
            title='Segments',
            form=form,
            status=400,
            errors=ui_errors(form),
        )
    return _render_unavailable(request, title='Segments', form=form, status=503)


@login_required
@require_GET
def segment_members_page(request: HttpRequest, segment_id: str) -> HttpResponse:
    form = SegmentMembersFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        return _render_unavailable(
            request,
            title='Segment Members',
            form=form,
            status=400,
            errors=ui_errors(form),
            values={'segment_id': segment_id},
        )
    return _render_unavailable(
        request,
        title='Segment Members',
        form=form,
        status=503,
        values={'segment_id': segment_id},
    )

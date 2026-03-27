from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.presenters import read_pagination, unavailable_context


def _render_unavailable(
    request: HttpRequest,
    *,
    title: str,
    values: dict[str, str],
) -> HttpResponse:
    context = unavailable_context(
        title=title,
        message='usecase wiring pending',
        values=values,
    )
    return render(request, 'backoffice/unavailable.html', context, status=503)


@login_required
@require_GET
def segments_page(request: HttpRequest) -> HttpResponse:
    values: dict[str, str] = {}
    try:
        pagination = read_pagination(request)
    except ValueError:
        values['query'] = 'invalid query'
    else:
        values['limit'] = str(pagination.limit)
        values['offset'] = str(pagination.offset)
    return _render_unavailable(request, title='Segments', values=values)


@login_required
@require_GET
def segment_members_page(request: HttpRequest, segment_id: str) -> HttpResponse:
    values = {'segment_id': segment_id}
    try:
        pagination = read_pagination(request)
    except ValueError:
        values['query'] = 'invalid query'
    else:
        values['limit'] = str(pagination.limit)
        values['offset'] = str(pagination.offset)
    return _render_unavailable(request, title='Segment Members', values=values)

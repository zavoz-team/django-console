from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.presenters import read_pagination, unavailable_context


@login_required
@require_GET
def jobs_page(request: HttpRequest) -> HttpResponse:
    values: dict[str, str] = {}
    try:
        pagination = read_pagination(request)
    except ValueError:
        values['query'] = 'invalid query'
    else:
        values['limit'] = str(pagination.limit)
        values['offset'] = str(pagination.offset)
    context = unavailable_context(
        title='Jobs',
        message='usecase wiring pending',
        values=values,
    )
    return render(request, 'backoffice/unavailable.html', context, status=503)

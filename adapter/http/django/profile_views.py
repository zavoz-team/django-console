from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.presenters import read_text, unavailable_context


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
def profiles_page(request: HttpRequest) -> HttpResponse:
    values: dict[str, str] = {}
    email = read_text(request, 'email')
    external_id = read_text(request, 'external_id')
    segment = read_text(request, 'segment')
    if email is not None:
        values['email'] = email
    if external_id is not None:
        values['external_id'] = external_id
    if segment is not None:
        values['segment'] = segment
    return _render_unavailable(request, title='Profiles', values=values)


@login_required
@require_GET
def profile_page(request: HttpRequest, customer_id: str) -> HttpResponse:
    return _render_unavailable(
        request,
        title='Profile',
        values={'customer_id': customer_id},
    )

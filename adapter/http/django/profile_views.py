from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.forms import ProfileFilterForm
from adapter.http.django.presenters import ui_context, ui_errors


def _render_unavailable(
    request: HttpRequest,
    *,
    title: str,
    form: ProfileFilterForm,
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
def profiles_page(request: HttpRequest) -> HttpResponse:
    form = ProfileFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        return _render_unavailable(
            request,
            title='Profiles',
            form=form,
            status=400,
            errors=ui_errors(form),
        )
    return _render_unavailable(request, title='Profiles', form=form, status=503)


@login_required
@require_GET
def profile_page(request: HttpRequest, customer_id: str) -> HttpResponse:
    form = ProfileFilterForm()
    return _render_unavailable(
        request,
        title='Profile',
        form=form,
        status=503,
        values={'customer_id': customer_id},
    )

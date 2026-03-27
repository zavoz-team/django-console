from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.forms import JobsFilterForm
from adapter.http.django.presenters import ui_context, ui_errors


@login_required
@require_GET
def jobs_page(request: HttpRequest) -> HttpResponse:
    form = JobsFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        context = ui_context(
            title='Jobs',
            errors=ui_errors(form),
            form=form,
        )
        return render(request, 'backoffice/unavailable.html', context, status=400)
    context = ui_context(
        title='Jobs',
        message='usecase wiring pending',
        form=form,
    )
    return render(request, 'backoffice/unavailable.html', context, status=503)

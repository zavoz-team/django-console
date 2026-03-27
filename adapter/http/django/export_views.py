from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from adapter.http.django.forms import ExportCreateForm
from adapter.http.django.presenters import ui_context, ui_errors


@login_required
@require_http_methods(['GET', 'POST'])
def exports_create_page(request: HttpRequest) -> HttpResponse:
    form = ExportCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        context = ui_context(
            title='Create Export',
            message='usecase wiring pending',
            form=form,
            errors=ui_errors(messages=('export unavailable',)),
        )
        return render(request, 'backoffice/export_create.html', context, status=503)

    if request.method == 'POST':
        context = ui_context(
            title='Create Export',
            form=form,
            errors=ui_errors(form),
        )
        return render(request, 'backoffice/export_create.html', context, status=400)

    context = ui_context(
        title='Create Export',
        message='usecase wiring pending',
        errors=[],
        form=form,
    )
    status = 200
    return render(request, 'backoffice/export_create.html', context, status=status)

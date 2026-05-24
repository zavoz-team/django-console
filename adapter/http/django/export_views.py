from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from adapter.http.django.forms import ExportCreateForm
from adapter.http.django.presenters import job_row, ui_context, ui_errors
from adapter.http.django.runtime import get_container
from domain.error import ExportTriggerError
from usecase.export_job import TriggerExportQuery


@login_required
@require_http_methods(['GET', 'POST'])
def exports_create_page(request: HttpRequest) -> HttpResponse:
    form = ExportCreateForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            context = ui_context(
                title='Create Export',
                form=form,
                errors=ui_errors(form),
            )
            return render(request, 'backoffice/export_create.html', context, status=400)

        try:
            actor_email = request.user.email or request.user.get_username()
            job = get_container().usecases.trigger_export.execute(
                TriggerExportQuery(
                    segment_id=form.cleaned_data['segment_id'],
                    destination_type=form.cleaned_data['destination_type'],
                    destination_url=form.cleaned_data['destination_url'],
                    actor_email=actor_email,
                    actor_id=(
                        str(request.user.pk) if request.user.pk is not None else None
                    ),
                )
            )
        except ExportTriggerError:
            context = ui_context(
                title='Create Export',
                form=form,
                errors=ui_errors(messages=('unavailable',)),
            )
            return render(request, 'backoffice/export_create.html', context, status=503)

        context = ui_context(
            title='Create Export',
            message='export started',
            form=form,
            extra={'job': job_row(job)},
        )
        return render(request, 'backoffice/export_create.html', context)

    context = ui_context(
        title='Create Export',
        form=form,
    )
    return render(request, 'backoffice/export_create.html', context)

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.forms import JobsFilterForm
from adapter.http.django.presenters import job_rows, ui_context, ui_errors
from adapter.http.django.runtime import get_container
from domain.error import CoreUnavailableError
from usecase.export_job import ListJobsQuery


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
        return render(request, 'backoffice/jobs.html', context, status=400)

    try:
        jobs = get_container().usecases.list_jobs.execute(
            ListJobsQuery(pagination=form.pagination())
        )
    except CoreUnavailableError:
        context = ui_context(
            title='Jobs',
            errors=ui_errors(messages=('unavailable',)),
            form=form,
        )
        return render(request, 'backoffice/jobs.html', context, status=503)

    context = ui_context(
        title='Jobs',
        form=form,
        extra={'rows': job_rows(list(jobs))},
    )
    return render(request, 'backoffice/jobs.html', context)

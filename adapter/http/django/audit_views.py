from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.presenters import audit_context, read_pagination
from adapter.http.django.runtime import get_container
from usecase.audit import ListAuditEntriesQuery


@login_required
@require_GET
def audit_page(request: HttpRequest) -> HttpResponse:
    try:
        pagination = read_pagination(request)
    except ValueError:
        context = audit_context(entries=[], limit=20, offset=0, error='invalid query')
        return render(request, 'backoffice/audit.html', context, status=400)

    entries = get_container().usecases.list_audit_entries.execute(
        ListAuditEntriesQuery(pagination=pagination)
    )
    context = audit_context(
        entries=entries,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return render(request, 'backoffice/audit.html', context)

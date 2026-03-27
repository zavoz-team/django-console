from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(['GET', 'POST'])
def exports_create_page(request: HttpRequest) -> HttpResponse:
    values = {
        'segment_id': request.POST.get('segment_id', '').strip(),
        'destination': request.POST.get('destination', '').strip(),
    }
    if request.method == 'POST':
        error(request, 'export unavailable')
    context = {
        'title': 'Create Export',
        'values': values,
        'message': 'usecase wiring pending',
    }
    status = 200 if request.method == 'GET' else 503
    return render(request, 'backoffice/export_create.html', context, status=status)

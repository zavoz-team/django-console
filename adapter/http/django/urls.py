from html import escape

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.views.decorators.http import require_GET

from .auth_views import login_view, logout_view
from .views import health


def _page(title: str, value: str | None = None) -> HttpResponse:
    body = '<main>'
    body += f'<h1>{escape(title)}</h1>'
    if value is not None:
        body += f'<p>{escape(value)}</p>'
    body += '</main>'
    return HttpResponse(
        '<!doctype html>'
        '<html lang="en">'
        '<head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{escape(title)}</title>'
        '</head>'
        f'<body>{body}</body>'
        '</html>'
    )


def _html_view(title: str, field_name: str | None = None):
    @login_required
    @require_GET
    def view(_: HttpRequest, **kwargs: str) -> HttpResponse:
        value = None
        if field_name is not None:
            value = kwargs[field_name]
        return _page(title, value)

    return view


profiles_page = _html_view('Profiles')
profile_page = _html_view('Profile', 'customer_id')
segments_page = _html_view('Segments')
segment_members_page = _html_view('Segment Members', 'segment_id')
jobs_page = _html_view('Jobs')
exports_create_page = _html_view('Create Export')
audit_page = _html_view('Audit')

public_urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/v1/health', health, name='health'),
]

internal_urlpatterns = [
    path('profiles/', profiles_page, name='profiles'),
    path('profiles/<str:customer_id>/', profile_page, name='profile'),
    path('segments/', segments_page, name='segments'),
    path(
        'segments/<str:segment_id>/members/',
        segment_members_page,
        name='segment_members',
    ),
    path('jobs/', jobs_page, name='jobs'),
    path('exports/create/', exports_create_page, name='exports_create'),
    path('audit/', audit_page, name='audit'),
]

urlpatterns = public_urlpatterns + internal_urlpatterns

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

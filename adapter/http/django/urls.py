from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import RedirectView

from .auth_views import login_view, logout_view
from .audit_views import audit_page
from .export_views import exports_create_page
from .job_views import jobs_page
from .profile_views import profile_page, profiles_page
from .segment_views import segment_members_page, segments_page
from .views import health

public_urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
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

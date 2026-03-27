from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from .auth_views import login_view, logout_view, operator_home
from .views import get_user, health

public_urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/v1/health', health, name='health'),
]

internal_urlpatterns = [
    path('admin/', admin.site.urls),
    path('operator/', operator_home, name='operator_home'),
    path('api/v1/users/<str:user_id>', get_user, name='get_user'),
]

urlpatterns = public_urlpatterns + internal_urlpatterns

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from .views import get_user, health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health', health, name='health'),
    path('api/v1/users/<str:user_id>', get_user, name='get_user'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

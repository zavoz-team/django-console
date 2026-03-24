from django.urls import path

from .views import get_user, health

urlpatterns = [
    path('api/v1/health', health, name='health'),
    path('api/v1/users/<str:user_id>', get_user, name='get_user'),
]

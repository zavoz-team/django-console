import os

from django.core.asgi import get_asgi_application

from adapter.http.django.runtime import initialize_runtime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adapter.http.django.settings')
initialize_runtime()

application = get_asgi_application()

import os

import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adapter.http.django.settings')

django.setup()

from adapter.http.django.runtime import initialize_runtime  # noqa: E402

initialize_runtime()
application = get_asgi_application()

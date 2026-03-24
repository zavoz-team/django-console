import os

import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adapter.http.django.settings')

django.setup()

from adapter.http.django.runtime import initialize_runtime  # noqa: E402

initialize_runtime()
application = get_wsgi_application()

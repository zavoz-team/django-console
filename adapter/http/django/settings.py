from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

SECRET_KEY = 'local'
DEBUG = True
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'repository.django.apps.RepositoryDjangoConfig',
]

MIDDLEWARE: list[str] = []

ROOT_URLCONF = 'adapter.http.django.urls'
ASGI_APPLICATION = 'adapter.http.django.asgi.application'
WSGI_APPLICATION = 'adapter.http.django.wsgi.application'

TEMPLATES: list[dict[str, object]] = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

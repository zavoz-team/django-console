from pathlib import Path

from adapter.config.model import DatabaseConfig
from adapter.http.django.runtime import get_config

BASE_DIR = Path(__file__).resolve().parents[3]


def _build_database(config: DatabaseConfig) -> dict[str, object]:
    if config.engine == 'sqlite':
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _build_sqlite_name(config.name),
        }

    data: dict[str, object] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.name,
    }
    if config.host is not None:
        data['HOST'] = config.host
    if config.port is not None:
        data['PORT'] = config.port
    if config.user is not None:
        data['USER'] = config.user
    if config.password is not None:
        data['PASSWORD'] = config.password
    return data


def _build_sqlite_name(name: str) -> Path:
    path = Path(name)
    if path.is_absolute():
        return path
    return BASE_DIR / path


APP_CONFIG = get_config()

SECRET_KEY = APP_CONFIG.security.signing_key
DEBUG = APP_CONFIG.app.env != 'prod'
ALLOWED_HOSTS = ['*']

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
DATABASES = {'default': _build_database(APP_CONFIG.database)}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

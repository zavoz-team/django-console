# Django Console

- Django как текущий HTTP-адаптер
- `domain/`, `usecase/`, `repository/`, `adapter/` с направлением зависимостей внутрь
- общий контейнер зависимостей, который создается один раз на старте
- конфиг из `config/app.yaml` + переменные окружения + `.env`
- логгер, метрики и трейсы спрятаны за интерфейсами
- Django ORM изолирован в `repository/django/`
- Django admin на `/admin/`
- API v1 на `/api/v1`

## Структура проекта

```text
domain/                      доменные сущности и ошибки
usecase/                     use case и интерфейсы портов
repository/                  реализации репозиториев
repository/django/           Django ORM модели и Django-репозиторий
adapter/config/              загрузка и модели конфига
adapter/di/                  контейнер зависимостей
adapter/observability/       stdout/file/noop-адаптеры логов, метрик, трейсов
adapter/otel/                OTel-адаптеры
adapter/http/django/         текущий HTTP-адаптер Django
config/                      YAML-конфиг
main.py                      локальный entrypoint
manage.py                    Django management команды
```

## Основные правила

- `domain/` не импортирует ничего внутреннего
- `usecase/` может импортировать только `domain/`
- `repository/` и `adapter/` могут импортировать `usecase/` и `domain/`
- Django, ORM и OTel не должны попадать в `domain/` и `usecase/`
- view не ходит в ORM напрямую
- репозиторий возвращает доменные модели, а не Django records

## Быстрый старт

### 1. Установка

```bash
make install
```

### 2. Минимальный `.env`

`adapter/config/loader.py` требует `APP_API_TOKEN` и `APP_SIGNING_KEY`. Сейчас токен еще не проверяется в view, но для загрузки конфига эти переменные нужны

```env
APP_API_TOKEN=local-api-token
APP_SIGNING_KEY=local-signing-key
```

Если запускаете через `make run`, Makefile уже подставляет локальные значения по умолчанию

### 3. Миграции

```bash
uv run python manage.py migrate
```

### 4. Создать администратора

```bash
uv run python manage.py createsuperuser
```

### 5. Запуск приложения

```bash
make run
```

Приложение поднимается на `http://127.0.0.1:8123`

## Полезные команды

```bash
make lint
make typecheck
make test
make pre-commit
make compose-up
make compose-down
make compose-logs
```

## Текущие маршруты

- `GET /api/v1/health`
- `GET /api/v1/users/<user_id>`
- `GET /admin/`

Проверка:

```bash
curl http://127.0.0.1:8123/api/v1/health
curl http://127.0.0.1:8123/api/v1/users/u-1
```

## Как проходит запрос

На текущем коде поток такой:

1. Django route из `adapter/http/django/urls.py` вызывает view из `adapter/http/django/views.py`
2. view берет singleton-контейнер через `adapter/http/django/runtime.py`
3. view вызывает use case из `container.usecases`
4. use case работает только с интерфейсами из `usecase/interface.py`
5. конкретный репозиторий в контейнере сейчас - `repository/django/user.py`
6. репозиторий общается с ORM-моделью `repository/django/models.py`
7. ORM record мапится в доменную модель через `repository/django/dto.py`

На примере пользователя это выглядит так:

```text
HTTP -> Django view -> GetUser -> UserRepository -> DjangoUserRepository -> UserRecord
```

## Конфиг

Базовый конфиг лежит в `config/app.yaml`, а переменные окружения могут его переопределять

Примеры полезных переменных:

```env
APP_NAME=web-python-skelet
APP_ENV=local
APP_HTTP_HOST=0.0.0.0
APP_HTTP_PORT=8123

APP_DB_ENGINE=sqlite
APP_DB_NAME=db.sqlite3

APP_LOGGING_LEVEL=INFO
APP_LOGGING_OUTPUT=stdout
APP_LOGGING_FORMAT=json

APP_METRICS_ENABLED=false
APP_TRACING_ENABLED=false
```

Варианты `APP_LOGGING_OUTPUT`:

- `stdout`
- `file`
- `otel`

Если выбираете `file`, нужен еще путь:

```env
APP_LOGGING_OUTPUT=file
APP_LOGGING_FILE_PATH=var/app.log
```


## Как добавлять новую фичу

Ниже микропример: добавляем сущность `Project` и endpoint `GET /api/v1/projects/<project_id>`

### 1. Domain

В `domain/` живут только сущности и доменные ошибки

```python
# domain/project.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Project:
    id: str
    name: str
    owner_id: str
```

```python
# domain/error.py
class ProjectNotFoundError(DomainError): ...
```

Что важно:

- без Django imports
- без ORM-моделей
- без JSON/HTTP деталей

### 2. Интерфейс порта

Интерфейсы, которые нужны use case, описывайте в `usecase/interface.py`

```python
# usecase/interface.py
from typing import Protocol

from domain.project import Project


class ProjectRepository(Protocol):
    def get(self, project_id: str) -> Project | None: ...

    def save(self, project: Project) -> None: ...
```

Смысл простой: use case знает только контракт, но не знает, это память, Django ORM или внешний API

### 3. Use case

Use case живет в `usecase/` и работает через интерфейсы

```python
# usecase/project.py
from domain.error import ProjectNotFoundError
from domain.project import Project
from usecase.interface import Logger, ProjectRepository, Tracer


class GetProject:
    def __init__(
        self,
        repository: ProjectRepository,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._repository = repository
        self._logger = logger
        self._tracer = tracer

    def execute(self, project_id: str) -> Project:
        with self._tracer.start_span(
            'usecase.get_project',
            attrs={'project.id': project_id},
        ) as span:
            project = self._repository.get(project_id)
            if project is None:
                error = ProjectNotFoundError(project_id)
                span.record_error(error)
                self._logger.warning(
                    'project_not_found',
                    attrs={'project_id': project_id},
                )
                raise error

            return project
```

Правило: use case не должен импортировать Django, `JsonResponse`, `models.Model` или `UserRecord`

### 4. ORM-модель и dto

Если данные лежат в БД, ORM держим только в `repository/django/`

```python
# repository/django/models.py
from django.db import models


class ProjectRecord(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    owner_id = models.CharField(max_length=255, db_index=True)
```

```python
# repository/django/dto.py
from domain.project import Project
from repository.django.models import ProjectRecord


def to_domain_project(record: ProjectRecord) -> Project:
    return Project(id=record.id, name=record.name, owner_id=record.owner_id)


def to_project_record_data(project: Project) -> dict[str, str]:
    return {'name': project.name, 'owner_id': project.owner_id}
```

Идея такая же, как у текущего `User`: record -> domain и domain -> data для `update_or_create`

### 5. Repository

Реализация репозитория зависит от Django ORM, но снаружи отдает только доменные модели.

```python
# repository/django/project.py
from domain.project import Project
from repository.django.dto import to_domain_project, to_project_record_data
from repository.django.models import ProjectRecord
from usecase.interface import ProjectRepository, Tracer


class DjangoProjectRepository(ProjectRepository):
    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def get(self, project_id: str) -> Project | None:
        with self._tracer.start_span(
            'repository.project',
            attrs={'project.id': project_id},
        ):
            record = ProjectRecord.objects.filter(id=project_id).first()
            if record is None:
                return None
            return to_domain_project(record)

    def save(self, project: Project) -> None:
        with self._tracer.start_span(
            'repository.project.save',
            attrs={'project.id': project.id},
        ):
            ProjectRecord.objects.update_or_create(
                id=project.id,
                defaults=to_project_record_data(project),
            )
```

Правильно:

- ORM-запросы только здесь
- mapping только здесь
- наружу возвращается `Project`

Неправильно:

- вернуть `ProjectRecord` в use case
- дергать `ProjectRecord.objects...` из view
- хранить бизнес-правила в репозитории

### 6. Wiring в контейнере

Репозиторий и use case нужно создать один раз в `adapter/di/container.py`

Микропример:

```python
@dataclass(frozen=True, slots=True)
class AppRepositories:
    user: UserRepository
    project: ProjectRepository


@dataclass(frozen=True, slots=True)
class AppUsecases:
    get_user: GetUser
    get_project: GetProject
```

```python
project_repository = DjangoProjectRepository(observability.tracer)

repositories = AppRepositories(
    user=user_repository,
    project=project_repository,
)

usecases = AppUsecases(
    get_user=GetUser(...),
    get_project=GetProject(
        repository=project_repository,
        logger=observability.logger,
        tracer=observability.tracer,
    ),
)
```

Не создавайте репозиторий внутри view на каждый запрос.

### 7. Django endpoint

View остается тонким: взял вход, вызвал use case, перевел доменную ошибку в HTTP-ответ

```python
# adapter/http/django/views.py
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from adapter.http.django.runtime import get_container
from domain.error import ProjectNotFoundError
from usecase.project import GetProjectQuery


@require_GET
def get_project(_: HttpRequest, project_id: str) -> JsonResponse:
    try:
        project = get_container().usecases.get_project.execute(project_id)
    except ProjectNotFoundError as exc:
        return JsonResponse({'detail': str(exc)}, status=404)

    return JsonResponse(
        {'id': project.id, 'name': project.name, 'owner_id': project.owner_id}
    )
```

И зарегистрировать маршрут:

```python
# adapter/http/django/urls.py
path('api/v1/projects/<str:project_id>', get_project, name='get_project')
```

### 8. Миграции

После добавления новых ORM-моделей:

```bash
uv run python manage.py makemigrations repository_django
uv run python manage.py migrate
```

### 9. Admin

Если модель должна быть видна в Django admin, регистрируйте ее в `repository/django/admin.py`

```python
from django.contrib import admin

from repository.django.models import ProjectRecord

admin.site.register(ProjectRecord)
```

## Как взаимодействовать с ORM

В этом проекте ORM - это деталь инфраструктуры, а не часть домена

Используйте такой шаблон

1. описали `models.Model` в `repository/django/models.py`
2. добавили mapper-функции в `repository/django/dto.py`
3. реализовали репозиторий в `repository/django/`
4. вернули наружу доменную модель

Микропримеры запросов:

```python
record = UserRecord.objects.filter(id=user_id).first()
```

```python
UserRecord.objects.update_or_create(
    id=user.id,
    defaults={'email': user.email, 'name': user.name},
)
```

Если нужно выполнить ad-hoc проверку в shell:

```bash
uv run python manage.py shell
```

```python
from repository.django.models import UserRecord

UserRecord.objects.all()
UserRecord.objects.filter(email='demo@example.com').first()
```

Но в приложении такие вызовы должны жить не во view и не в use case, а в repository

## Как писать логи

Писать логи нужно через интерфейс `Logger` из `usecase/interface.py`.

Текущий рабочий пример - `usecase/user.py`:

```python
self._logger.warning(
    'user_not_found',
    attrs={'user_id': query.user_id},
)
```

Рекомендации:

- сообщение короткое и стабильное, например `user_not_found`
- детали кладем в `attrs`
- `attrs` должны быть простых типов: `str | int | float | bool`

Микропример информационного лога:

```python
self._logger.info(
    'project_created',
    attrs={'project.id': project.id, 'owner_id': project.owner_id},
)
```

### Куда уходят логи

Выбор делается через конфиг:

- `stdout` -> `adapter/observability/logging.py`
- `file` -> `adapter/observability/logging.py`
- `otel` -> `adapter/otel/logging.py`

Пример для stdout JSON:

```env
APP_LOGGING_OUTPUT=stdout
APP_LOGGING_FORMAT=json
APP_LOGGING_LEVEL=INFO
```

Пример строки лога:

```json
{"attrs":{"user_id":"u-404"},"level":"WARNING","message":"user_not_found","timestamp":"2026-03-24T12:00:00.000Z"}
```

Пример для файла:

```env
APP_LOGGING_OUTPUT=file
APP_LOGGING_FILE_PATH=var/app.log
APP_LOGGING_FORMAT=text
```

## Как писать spans и метрики

Трейсы тоже идут через интерфейс, не напрямую через OpenTelemetry API в use case.

Микропример:

```python
with self._tracer.start_span(
    'usecase.create_project',
    attrs={'project.id': command.project_id},
) as span:
    ...
    span.set_attribute('project.owner_id', command.owner_id)
```

Если ловите ошибку и хотите явно записать ее в span:

```python
span.record_error(error)
```

Интерфейс метрик тоже есть в `usecase/interface.py`, но в текущем `GetUser` он еще не используется. Если добавите use case с метриками, прокиньте `Metrics` через контейнер так же, как `Logger` и `Tracer`

## Django runtime и singleton-контейнер

Точка входа сейчас такая:

- `main.py` запускает Uvicorn
- `adapter/http/django/asgi.py` вызывает `initialize_runtime()`
- `adapter/http/django/runtime.py` создает контейнер один раз
- `adapter/di/container.py` создает репозитории и use case один раз

Это значит:

- зависимости не создаются на каждый запрос
- view не занимается ручной сборкой объектов
- observability shutdown вызывается централизованно

## OTel и Docker

Для Docker-режима есть `make compose-up`. В `docker-compose.yml` приложение запускается сразу с OTel и UI Grafana LGTM доступен на `http://127.0.0.1:3000`

Команда `make run-otel` подходит для локального запуска приложения, если у вас уже есть collector на `localhost:4318`

## Что лучше не делать

- не импортировать `django.*` в `domain/` и `usecase/`
- не вызывать ORM из `adapter/http/django/views.py`
- не прокидывать `HttpRequest` в use case
- не возвращать `JsonResponse` из use case
- не логировать через `print()` внутри use case
- не писать OTel-специфичный код в домене

## Короткая шпаргалка по слоям

- `domain/` -> что такое сущность и какие у нее ошибки
- `usecase/` -> что система делает
- `repository/` -> как система получает и сохраняет данные
- `adapter/http/django/` -> как HTTP превращается во вход use case
- `adapter/di/` -> где все связывается вместе

Если сомневаетесь, куда положить код, задайте вопрос так: это бизнес-правило или инфраструктура? Бизнес-правило идет внутрь, инфраструктура остается снаружи

# django-console

Внутренний backoffice сервис CDP-платформы. Django-сервис на чистой архитектуре - принимает HTTP запросы, делегирует бизнес-логику в `cdp-core` через HTTP API и показывает оператору профили клиентов, сегменты, задания и audit log

## Место в системе

```
ingest-bridge (Flask)  -->  Kafka  -->  cdp-core (FastAPI)
                                              |
                                    django-console (Django)  <-- оператор
```

- `cdp-core` - единственный владелец доменных данных
- `django-console` работает с `cdp-core` только через HTTP API, своей доменной логики не содержит
- все страницы требуют авторизации Django

## Структура проекта

```text
domain/                        доменные типы и ошибки (без Django)
usecase/                       use case и интерфейсы портов
usecase/interface.py           Protocol-интерфейсы: Logger, Tracer, Metrics, репозитории
repository/                    реализации репозиториев
adapter/config/                загрузка конфига из YAML + env
adapter/di/                    DI-контейнер, собирается один раз на старте
adapter/observability/         stdout / file / noop адаптеры логов и трейсов
adapter/otel/                  OTel адаптеры (bootstrap, logging, metrics, tracing)
adapter/http/django/           Django HTTP адаптер: views, urls, templates, settings
adapter/http/fastapi/          FastAPI API адаптер (health, v1 router)
config/app.yaml                базовый конфиг
main.py                        точка входа - запускает Uvicorn
manage.py                      Django management команды
```

## Правила слоев

- `domain/` не импортирует ничего внутреннего
- `usecase/` импортирует только `domain/`
- `repository/` и `adapter/` импортируют `usecase/` и `domain/`
- Django, ORM и OTel не попадают в `domain/` и `usecase/`
- view не ходит в ORM напрямую
- view не принимает `HttpRequest` в use case

## Быстрый старт

### 1. Зависимости

```bash
make install
```

Используется [uv](https://github.com/astral-sh/uv). Python >= 3.13.

### 2. Переменные окружения

Скопируйте `.env.example` и заполните:

```bash
cp .env.example .env
```

Минимальный набор:

```env
APP_API_TOKEN=local-api-token
APP_SIGNING_KEY=local-signing-key
APP_CORE_API_SERVICE_TOKEN=local-service-token
```

Если запускаете через `make run` - Makefile подставляет локальные значения автоматически.

### 3. Миграции

```bash
uv run python manage.py migrate
```

### 4. Создать администратора

```bash
uv run python manage.py createsuperuser
```

### 5. Запуск

```bash
make run
```

Сервис поднимается на `http://127.0.0.1:8123`. Корень `/` редиректит на `/login/`.

## Команды

```bash
make install        # установить зависимости
make run            # запустить локально
make run-otel       # запустить с локальным OTel collector
make lint           # ruff check
make typecheck      # mypy
make test           # pytest
make pre-commit     # lint + typecheck + test

make compose-build  # собрать Docker образы
make compose-up     # поднять приложение + OTel collector + Grafana
make compose-down   # остановить compose стек
make compose-logs   # хвост логов app и otel-collector
make compose-ps     # статус compose сервисов
```

## Маршруты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | редирект на `/login/` |
| GET/POST | `/login/` | страница авторизации |
| GET | `/logout/` | выход |
| GET | `/api/v1/health` | health check |
| GET | `/profiles/` | список клиентских профилей |
| GET | `/profiles/<customer_id>/` | профиль клиента (Customer 360 Lite) |
| GET | `/segments/` | список сегментов |
| GET | `/segments/<segment_id>/members/` | участники сегмента |
| GET | `/jobs/` | список заданий |
| GET | `/exports/create/` | создать экспорт |
| GET | `/audit/` | audit log |

Проверка health:

```bash
curl http://127.0.0.1:8123/api/v1/health
```

## Конфигурация

Базовый конфиг - `config/app.yaml`. Переменные окружения с префиксом `APP_` его переопределяют.

```yaml
http:
  host: 0.0.0.0
  port: 8123

database:
  engine: sqlite     # sqlite | postgresql
  name: db.sqlite3

logging:
  level: INFO
  output: stdout     # stdout | file | otel
  format: json       # json | text

metrics:
  enabled: false

tracing:
  enabled: false
```

Полный список env переменных:

```env
APP_NAME=web-python-skelet
APP_ENV=local

APP_HTTP_HOST=0.0.0.0
APP_HTTP_PORT=8123

APP_DB_ENGINE=sqlite
APP_DB_NAME=db.sqlite3

APP_LOGGING_LEVEL=INFO
APP_LOGGING_OUTPUT=stdout    # stdout | file | otel
APP_LOGGING_FORMAT=json

APP_METRICS_ENABLED=false
APP_TRACING_ENABLED=false

# нужны только при APP_LOGGING_OUTPUT=otel или APP_TRACING_ENABLED=true
APP_OTEL_LOGS_ENDPOINT=http://localhost:4318/v1/logs
APP_OTEL_METRICS_ENDPOINT=http://localhost:4318/v1/metrics
APP_OTEL_TRACES_ENDPOINT=http://localhost:4318/v1/traces
OTEL_METRIC_EXPORT_INTERVAL=1000

# подключение к cdp-core
APP_CORE_API_BASE_URL=http://localhost:8080
APP_CORE_API_SERVICE_TOKEN=local-service-token
```

Если выбран вывод логов в файл:

```env
APP_LOGGING_OUTPUT=file
APP_LOGGING_FILE_PATH=var/app.log
```

## Docker Compose

Запускает сервис вместе с Grafana LGTM (OTel Collector + Loki + Tempo + Prometheus + Grafana):

```bash
make compose-up
```

- приложение: `http://127.0.0.1:8123`
- Grafana: `http://127.0.0.1:3000`

Для compose нужен `.env` с обязательными переменными - `APP_API_TOKEN`, `APP_SIGNING_KEY`, `APP_CORE_API_SERVICE_TOKEN`, `DJANGO_SUPERUSER_PASSWORD`.

## Observability

Трейсинг и метрики реализованы через интерфейсы из `usecase/interface.py`. Use case и репозитории не импортируют OpenTelemetry напрямую.

Логи структурированные в формате JSON:

```json
{"attrs": {"user_id": "u-404"}, "level": "WARNING", "message": "user_not_found", "timestamp": "2026-05-24T12:00:00.000Z"}
```

Трейс в use case:

```python
with self._tracer.start_span('usecase.get_profile', attrs={'customer.id': customer_id}) as span:
    ...
    span.record_error(error)
```

## Добавление новой фичи

Короткая схема:

```
domain/entity.py          -> доменная сущность и ошибки
usecase/interface.py      -> Protocol-интерфейс репозитория
usecase/entity.py         -> use case через интерфейсы
repository/django/        -> ORM модель + dto + репозиторий
adapter/di/container.py   -> создать репозиторий и use case один раз
adapter/http/django/      -> тонкий view + url
```

Правило: бизнес-правило идет в `domain/` и `usecase/`, инфраструктура остается в `adapter/` и `repository/`.

## Технологии

| Слой | Технология |
|------|-----------|
| HTTP сервер | Django |
| Dependency management | uv |
| Observability | OpenTelemetry SDK |
| Lint | ruff |
| Types | mypy |
| Tests | pytest |
| Container | Docker + Compose |

import os
from collections.abc import Mapping
from pathlib import Path

import yaml
from dotenv import dotenv_values

from .model import (
    AppConfig,
    AppSectionConfig,
    CoreApiConfig,
    DatabaseConfig,
    HttpConfig,
    LoggingConfig,
    MetricsConfig,
    OtelConfig,
    SecurityConfig,
    TracingConfig,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / 'config' / 'app.yaml'
DEFAULT_DOTENV_PATH = ROOT_DIR / '.env'


class ConfigError(ValueError):
    pass


def load_config(
    config_path: Path | str | None = None,
    env_path: Path | str | None = None,
    environ: Mapping[str, str] | None = None,
) -> AppConfig:
    yaml_data = _load_yaml(_path_or_default(config_path, DEFAULT_CONFIG_PATH))
    env_values = _load_env(_path_or_default(env_path, DEFAULT_DOTENV_PATH), environ)

    app_section = _section(yaml_data, 'app')
    http_section = _section(yaml_data, 'http')
    database_section = _section(yaml_data, 'database')
    logging_section = _section(yaml_data, 'logging')
    metrics_section = _section(yaml_data, 'metrics')
    tracing_section = _section(yaml_data, 'tracing')
    security_section = _section(yaml_data, 'security')
    core_api_section = _section(yaml_data, 'core_api')

    logging_output = _yaml_or_env_choice(
        logging_section,
        'output',
        'logging.output',
        env_values,
        {'stdout', 'file', 'otel'},
        'APP_LOGGING_OUTPUT',
    )

    logging_format = _yaml_or_env_choice(
        logging_section,
        'format',
        'logging.format',
        env_values,
        {'text', 'json'},
        'APP_LOGGING_FORMAT',
    )

    metrics_enabled = _yaml_or_env_bool(
        metrics_section,
        'enabled',
        'metrics.enabled',
        env_values,
        'APP_METRICS_ENABLED',
    )

    tracing_enabled = _yaml_or_env_bool(
        tracing_section,
        'enabled',
        'tracing.enabled',
        env_values,
        'APP_TRACING_ENABLED',
    )

    return AppConfig(
        app=AppSectionConfig(
            name=_yaml_or_env_str(
                app_section, 'name', 'app.name', env_values, 'APP_NAME'
            ),
            env=_yaml_or_env_str(app_section, 'env', 'app.env', env_values, 'APP_ENV'),
        ),
        http=HttpConfig(
            host=_yaml_or_env_str(
                http_section,
                'host',
                'http.host',
                env_values,
                'APP_HTTP_HOST',
            ),
            port=_yaml_or_env_int(
                http_section,
                'port',
                'http.port',
                env_values,
                'APP_HTTP_PORT',
            ),
        ),
        database=DatabaseConfig(
            engine=_yaml_or_env_choice(
                database_section,
                'engine',
                'database.engine',
                env_values,
                {'sqlite', 'postgresql'},
                'APP_DB_ENGINE',
            ),
            name=_yaml_or_env_str(
                database_section,
                'name',
                'database.name',
                env_values,
                'APP_DB_NAME',
            ),
            host=_yaml_or_env_optional_str(
                database_section,
                'host',
                env_values,
                'APP_DB_HOST',
            ),
            port=_yaml_or_env_optional_int(
                database_section,
                'port',
                env_values,
                'APP_DB_PORT',
            ),
            user=_yaml_or_env_optional_str(
                database_section,
                'user',
                env_values,
                'APP_DB_USER',
            ),
            password=_yaml_or_env_optional_str(
                database_section,
                'password',
                env_values,
                'APP_DB_PASSWORD',
            ),
        ),
        logging=LoggingConfig(
            level=_yaml_or_env_str(
                logging_section,
                'level',
                'logging.level',
                env_values,
                'APP_LOGGING_LEVEL',
            ),
            output=logging_output,
            format=logging_format,
            file_path=(
                None
                if logging_output != 'file'
                else _yaml_or_env_str(
                    logging_section,
                    'file_path',
                    'logging.file_path',
                    env_values,
                    'APP_LOGGING_FILE_PATH',
                )
            ),
        ),
        metrics=MetricsConfig(enabled=metrics_enabled),
        tracing=TracingConfig(enabled=tracing_enabled),
        otel=_load_otel_config(
            yaml_data,
            env_values,
            enable_logs=logging_output == 'otel',
            enable_metrics=metrics_enabled,
            enable_tracing=tracing_enabled,
        ),
        security=SecurityConfig(
            token_header=_yaml_or_env_str(
                security_section,
                'token_header',
                'security.token_header',
                env_values,
                'APP_API_TOKEN_HEADER',
            ),
            api_token=_env_str(env_values, 'APP_API_TOKEN'),
            signing_key=_env_str(env_values, 'APP_SIGNING_KEY'),
        ),
        core_api=CoreApiConfig(
            base_url=_yaml_or_env_str(
                core_api_section,
                'base_url',
                'core_api.base_url',
                env_values,
                'APP_CORE_API_BASE_URL',
            ),
            timeout_seconds=_yaml_or_env_int(
                core_api_section,
                'timeout_seconds',
                'core_api.timeout_seconds',
                env_values,
                'APP_CORE_API_TIMEOUT_SECONDS',
            ),
            service_token_header=_yaml_or_env_str(
                core_api_section,
                'service_token_header',
                'core_api.service_token_header',
                env_values,
                'APP_CORE_API_SERVICE_TOKEN_HEADER',
            ),
            service_token=_env_str(env_values, 'APP_CORE_API_SERVICE_TOKEN'),
            retry_attempts=_yaml_or_env_optional_int(
                core_api_section,
                'retry_attempts',
                env_values,
                'APP_CORE_API_RETRY_ATTEMPTS',
            ),
            retry_backoff_ms=_yaml_or_env_optional_int(
                core_api_section,
                'retry_backoff_ms',
                env_values,
                'APP_CORE_API_RETRY_BACKOFF_MS',
            ),
        ),
    )


def _path_or_default(path_value: Path | str | None, default: Path) -> Path:
    if path_value is None:
        return default
    return Path(path_value)


def _load_yaml(path: Path) -> dict[str, object]:
    try:
        with path.open(encoding='utf-8') as file:
            loaded = yaml.safe_load(file)
    except FileNotFoundError as exc:
        raise ConfigError(f'missing {_display_path(path)}') from exc

    if loaded is None:
        raise ConfigError('empty config')
    if not isinstance(loaded, dict):
        raise ConfigError('invalid root')

    data: dict[str, object] = {}
    for key, value in loaded.items():
        if not isinstance(key, str):
            raise ConfigError('invalid root')
        data[key] = value
    return data


def _load_env(
    env_path: Path,
    environ: Mapping[str, str] | None,
) -> dict[str, str]:
    values = _read_dotenv(env_path)
    source = os.environ if environ is None else environ
    for key, value in source.items():
        values[key] = value
    return values


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for key, value in dotenv_values(path).items():
        if value is None:
            continue
        values[key] = value
    return values


def _section(data: Mapping[str, object], name: str) -> dict[str, object]:
    value = data.get(name)
    if value is None:
        raise ConfigError(f'missing {name}')
    if not isinstance(value, dict):
        raise ConfigError(f'invalid {name}')

    section: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ConfigError(f'invalid {name}')
        section[key] = item
    return section


def _optional_section(data: Mapping[str, object], name: str) -> dict[str, object]:
    value = data.get(name)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f'invalid {name}')

    section: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ConfigError(f'invalid {name}')
        section[key] = item
    return section


def _load_otel_config(
    data: Mapping[str, object],
    env: Mapping[str, str],
    *,
    enable_logs: bool,
    enable_metrics: bool,
    enable_tracing: bool,
) -> OtelConfig:
    if not any((enable_logs, enable_metrics, enable_tracing)):
        return OtelConfig(
            service_name='',
            logs_endpoint='',
            metrics_endpoint='',
            traces_endpoint='',
            metric_export_interval=0,
        )

    otel_section = _optional_section(data, 'otel')
    service_name = _yaml_or_env_str(
        otel_section,
        'service_name',
        'otel.service_name',
        env,
        'APP_OTEL_SERVICE_NAME',
    )
    logs_endpoint = ''
    metrics_endpoint = ''
    traces_endpoint = ''
    metric_export_interval = 0

    if enable_logs:
        logs_endpoint = _yaml_or_env_str(
            otel_section,
            'logs_endpoint',
            'otel.logs_endpoint',
            env,
            'APP_OTEL_LOGS_ENDPOINT',
        )

    if enable_metrics:
        metrics_endpoint = _yaml_or_env_str(
            otel_section,
            'metrics_endpoint',
            'otel.metrics_endpoint',
            env,
            'APP_OTEL_METRICS_ENDPOINT',
        )
        metric_export_interval = _yaml_or_env_int(
            otel_section,
            'metric_export_interval',
            'otel.metric_export_interval',
            env,
            'OTEL_METRIC_EXPORT_INTERVAL',
        )

    if enable_tracing:
        traces_endpoint = _yaml_or_env_str(
            otel_section,
            'traces_endpoint',
            'otel.traces_endpoint',
            env,
            'APP_OTEL_TRACES_ENDPOINT',
        )

    return OtelConfig(
        service_name=service_name,
        logs_endpoint=logs_endpoint,
        metrics_endpoint=metrics_endpoint,
        traces_endpoint=traces_endpoint,
        metric_export_interval=metric_export_interval,
    )


def _yaml_or_env_str(
    section: Mapping[str, object],
    field_name: str,
    label: str,
    env: Mapping[str, str],
    env_name: str | None = None,
) -> str:
    if env_name is not None and env_name in env:
        return _as_str(env[env_name], env_name)
    if field_name not in section:
        raise ConfigError(f'missing {label}')
    return _as_str(section[field_name], label)


def _yaml_or_env_int(
    section: Mapping[str, object],
    field_name: str,
    label: str,
    env: Mapping[str, str],
    env_name: str | None = None,
) -> int:
    if env_name is not None and env_name in env:
        return _as_int(env[env_name], env_name)
    if field_name not in section:
        raise ConfigError(f'missing {label}')
    return _as_int(section[field_name], label)


def _yaml_or_env_bool(
    section: Mapping[str, object],
    field_name: str,
    label: str,
    env: Mapping[str, str],
    env_name: str | None = None,
) -> bool:
    if env_name is not None and env_name in env:
        return _as_bool(env[env_name], env_name)
    if field_name not in section:
        raise ConfigError(f'missing {label}')
    return _as_bool(section[field_name], label)


def _yaml_or_env_choice(
    section: Mapping[str, object],
    field_name: str,
    label: str,
    env: Mapping[str, str],
    choices: set[str],
    env_name: str | None = None,
) -> str:
    value = _yaml_or_env_str(section, field_name, label, env, env_name)
    normalized = value.lower()
    if normalized not in choices:
        raise ConfigError(f'invalid {label}')
    return normalized


def _yaml_or_env_optional_str(
    section: Mapping[str, object],
    field_name: str,
    env: Mapping[str, str],
    env_name: str | None = None,
) -> str | None:
    if env_name is not None and env_name in env:
        return _as_optional_str(env[env_name], env_name)
    if field_name not in section:
        return None
    return _as_optional_str(section[field_name], field_name)


def _yaml_or_env_optional_int(
    section: Mapping[str, object],
    field_name: str,
    env: Mapping[str, str],
    env_name: str | None = None,
) -> int | None:
    if env_name is not None and env_name in env:
        return _as_optional_int(env[env_name], env_name)
    if field_name not in section:
        return None
    return _as_optional_int(section[field_name], field_name)


def _env_str(env: Mapping[str, str], name: str) -> str:
    if name not in env:
        raise ConfigError(f'missing {name}')
    return _as_str(env[name], name)


def _as_str(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ConfigError(f'invalid {label}')

    text = value.strip()
    if not text:
        raise ConfigError(f'invalid {label}')
    return text


def _as_optional_str(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f'invalid {label}')

    text = value.strip()
    if not text:
        return None
    return text


def _as_int(value: object, label: str) -> int:
    if isinstance(value, bool):
        raise ConfigError(f'invalid {label}')
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ConfigError(f'invalid {label}')
        try:
            return int(text)
        except ValueError as exc:
            raise ConfigError(f'invalid {label}') from exc
    raise ConfigError(f'invalid {label}')


def _as_optional_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
    return _as_int(value, label)


def _as_bool(value: object, label: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text == 'true':
            return True
        if text == 'false':
            return False
    raise ConfigError(f'invalid {label}')


def _display_path(path: Path) -> str:
    if path.is_relative_to(ROOT_DIR):
        return str(path.relative_to(ROOT_DIR))
    return str(path)

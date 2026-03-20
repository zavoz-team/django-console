import os
from collections.abc import Mapping
from pathlib import Path

import yaml
from dotenv import dotenv_values

from .model import (
    AppConfig,
    AppSectionConfig,
    HttpConfig,
    LoggingConfig,
    OtelConfig,
    SecurityConfig,
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
    logging_section = _section(yaml_data, 'logging')
    otel_section = _section(yaml_data, 'otel')
    security_section = _section(yaml_data, 'security')

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
            api_prefix=_yaml_or_env_str(
                http_section,
                'api_prefix',
                'http.api_prefix',
                env_values,
                'APP_HTTP_API_PREFIX',
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
        ),
        otel=OtelConfig(
            service_name=_yaml_or_env_str(
                otel_section,
                'service_name',
                'otel.service_name',
                env_values,
                'APP_OTEL_SERVICE_NAME',
            ),
            logs_endpoint=_yaml_or_env_str(
                otel_section,
                'logs_endpoint',
                'otel.logs_endpoint',
                env_values,
                'APP_OTEL_LOGS_ENDPOINT',
            ),
            metrics_endpoint=_yaml_or_env_str(
                otel_section,
                'metrics_endpoint',
                'otel.metrics_endpoint',
                env_values,
                'APP_OTEL_METRICS_ENDPOINT',
            ),
            traces_endpoint=_yaml_or_env_str(
                otel_section,
                'traces_endpoint',
                'otel.traces_endpoint',
                env_values,
                'APP_OTEL_TRACES_ENDPOINT',
            ),
            metric_export_interval=_yaml_or_env_int(
                otel_section,
                'metric_export_interval',
                'otel.metric_export_interval',
                env_values,
                'OTEL_METRIC_EXPORT_INTERVAL',
            ),
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


def _display_path(path: Path) -> str:
    if path.is_relative_to(ROOT_DIR):
        return str(path.relative_to(ROOT_DIR))
    return str(path)

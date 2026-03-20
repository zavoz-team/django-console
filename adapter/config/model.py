from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppSectionConfig:
    name: str
    env: str


@dataclass(frozen=True, slots=True)
class HttpConfig:
    host: str
    port: int


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str
    output: str
    format: str
    file_path: str | None


@dataclass(frozen=True, slots=True)
class MetricsConfig:
    enabled: bool


@dataclass(frozen=True, slots=True)
class TracingConfig:
    enabled: bool


@dataclass(frozen=True, slots=True)
class OtelConfig:
    service_name: str
    logs_endpoint: str
    metrics_endpoint: str
    traces_endpoint: str
    metric_export_interval: int


@dataclass(frozen=True, slots=True)
class SecurityConfig:
    token_header: str
    api_token: str
    signing_key: str


@dataclass(frozen=True, slots=True)
class AppConfig:
    app: AppSectionConfig
    http: HttpConfig
    logging: LoggingConfig
    metrics: MetricsConfig
    tracing: TracingConfig
    otel: OtelConfig
    security: SecurityConfig

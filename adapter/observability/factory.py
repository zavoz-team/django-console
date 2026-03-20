from collections.abc import Callable

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from adapter.config.model import AppConfig
from adapter.otel.bootstrap import OtelRuntime, setup_otel
from usecase.interface import Logger, Metrics, Tracer

from .logging import FileLogger, StdoutLogger
from .noop import NoopMetrics, NoopTracer
from .runtime import ObservabilityRuntime


def build_observability(config: AppConfig) -> ObservabilityRuntime:
    otel_runtime = _setup_otel_runtime(config)

    try:
        logger, logger_shutdown = _build_logger(config, otel_runtime)
    except Exception:
        if otel_runtime is not None:
            otel_runtime.shutdown()
        raise

    metrics: Metrics = NoopMetrics()
    tracer: Tracer = NoopTracer()
    meter_provider: MeterProvider | None = None
    tracer_provider: TracerProvider | None = None
    shutdown_callback_list: list[Callable[[], None]] = []

    if logger_shutdown is not None:
        shutdown_callback_list.append(logger_shutdown)

    if otel_runtime is not None:
        meter_provider = otel_runtime.meter_provider
        tracer_provider = otel_runtime.tracer_provider
        shutdown_callback_list.append(otel_runtime.shutdown)

    if config.metrics.enabled:
        if otel_runtime is None or otel_runtime.metrics is None:
            raise ValueError('missing otel metrics')
        metrics = otel_runtime.metrics

    if config.tracing.enabled:
        if otel_runtime is None or otel_runtime.tracer is None:
            raise ValueError('missing otel tracer')
        tracer = otel_runtime.tracer

    return ObservabilityRuntime(
        logger=logger,
        metrics=metrics,
        tracer=tracer,
        meter_provider=meter_provider,
        tracer_provider=tracer_provider,
        _shutdown_callbacks=tuple(shutdown_callback_list),
    )


def _setup_otel_runtime(config: AppConfig) -> OtelRuntime | None:
    enable_logs = config.logging.output == 'otel'
    enable_metrics = config.metrics.enabled
    enable_tracing = config.tracing.enabled

    if not any((enable_logs, enable_metrics, enable_tracing)):
        return None

    return setup_otel(
        config,
        enable_logs=enable_logs,
        enable_metrics=enable_metrics,
        enable_tracing=enable_tracing,
    )


def _build_logger(
    config: AppConfig,
    otel_runtime: OtelRuntime | None,
) -> tuple[Logger, Callable[[], None] | None]:
    if config.logging.output == 'stdout':
        stdout_logger = StdoutLogger(
            f'{config.app.name}.stdout',
            config.logging.level,
            config.logging.format,
        )
        return stdout_logger, stdout_logger.shutdown
    if config.logging.output == 'file':
        file_path = config.logging.file_path
        if file_path is None:
            raise ValueError('missing logging.file_path')
        file_logger = FileLogger(
            file_path,
            f'{config.app.name}.file',
            config.logging.level,
            config.logging.format,
        )
        return file_logger, file_logger.shutdown
    if config.logging.output == 'otel':
        if otel_runtime is None or otel_runtime.logger is None:
            raise ValueError('missing otel logger')
        return otel_runtime.logger, None
    raise ValueError('invalid logging output')

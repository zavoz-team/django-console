from dataclasses import dataclass

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from adapter.config.model import AppConfig

from .logging import OtelLogger
from .metrics import OtelMetrics
from .tracing import OtelTracer


@dataclass(frozen=True, slots=True)
class OtelRuntime:
    logger_provider: LoggerProvider
    meter_provider: MeterProvider
    tracer_provider: TracerProvider
    logger: OtelLogger
    metrics: OtelMetrics
    tracer: OtelTracer

    def shutdown(self) -> None:
        self.meter_provider.shutdown()
        self.tracer_provider.shutdown()
        self.logger_provider.shutdown()


def setup_otel(config: AppConfig) -> OtelRuntime:
    if config.otel.metric_export_interval <= 0:
        raise ValueError('invalid metric export interval')

    resource = Resource.create(
        {
            'service.name': config.otel.service_name,
            'deployment.environment': config.app.env,
        }
    )

    logger_provider = LoggerProvider(resource=resource, shutdown_on_exit=False)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=config.otel.logs_endpoint))
    )

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=config.otel.metrics_endpoint),
        export_interval_millis=config.otel.metric_export_interval,
    )
    meter_provider = MeterProvider(
        metric_readers=[metric_reader],
        resource=resource,
        shutdown_on_exit=False,
    )

    tracer_provider = TracerProvider(resource=resource, shutdown_on_exit=False)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=config.otel.traces_endpoint))
    )

    set_logger_provider(logger_provider)
    metrics.set_meter_provider(meter_provider)
    trace.set_tracer_provider(tracer_provider)

    scope_name = config.app.name
    logger = OtelLogger(logger_provider.get_logger(scope_name), config.logging.level)
    metrics_adapter = OtelMetrics(meter_provider.get_meter(scope_name))
    tracer = OtelTracer(tracer_provider.get_tracer(scope_name))

    return OtelRuntime(
        logger_provider=logger_provider,
        meter_provider=meter_provider,
        tracer_provider=tracer_provider,
        logger=logger,
        metrics=metrics_adapter,
        tracer=tracer,
    )

import atexit
from dataclasses import dataclass

from opentelemetry.instrumentation.django import DjangoInstrumentor

from adapter.di.container import AppContainer, build_container
from adapter.http.django.config import get_config


@dataclass(slots=True)
class RuntimeState:
    container: AppContainer | None = None
    is_registered: bool = False


RUNTIME_STATE = RuntimeState()


def initialize_runtime() -> AppContainer:
    if RUNTIME_STATE.container is None:
        RUNTIME_STATE.container = build_container(config=get_config())
    if not RUNTIME_STATE.is_registered:
        atexit.register(shutdown_runtime)
        DjangoInstrumentor().instrument(
            tracer_provider=RUNTIME_STATE.container.observability.tracer_provider,
            meter_provider=RUNTIME_STATE.container.observability.meter_provider,
            exclude_spans=['send', 'receive'],
            excluded_urls='admin',
        )
        RUNTIME_STATE.is_registered = True
    if RUNTIME_STATE.container is None:
        raise RuntimeError('container unavailable')
    return RUNTIME_STATE.container


def get_container() -> AppContainer:
    return initialize_runtime()


def shutdown_runtime() -> None:
    if RUNTIME_STATE.container is None:
        return
    try:
        DjangoInstrumentor().uninstrument()
        RUNTIME_STATE.container.shutdown()
    finally:
        RUNTIME_STATE.container = None
        RUNTIME_STATE.is_registered = False

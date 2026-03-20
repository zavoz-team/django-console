from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from adapter.di.container import build_container
from adapter.http.fastapi.dependencies import APP_CONFIG_STATE, APP_CONTAINER_STATE
from fastapi import FastAPI


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    config = getattr(app.state, APP_CONFIG_STATE, None)
    if config is None:
        raise RuntimeError('config unavailable')

    container = build_container(config=config)
    instrumented = False
    setattr(app.state, APP_CONTAINER_STATE, container)

    try:
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=container.observability.tracer_provider,
        )
        instrumented = True
        yield
    finally:
        if instrumented:
            FastAPIInstrumentor.uninstrument_app(app)
        container.shutdown()

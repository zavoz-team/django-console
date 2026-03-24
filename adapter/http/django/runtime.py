import atexit
from dataclasses import dataclass

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
        RUNTIME_STATE.container.shutdown()
    finally:
        RUNTIME_STATE.container = None

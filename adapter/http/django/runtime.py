import atexit
from dataclasses import dataclass

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.di.container import AppContainer, build_container


@dataclass(slots=True)
class RuntimeState:
    config: AppConfig | None = None
    container: AppContainer | None = None
    is_registered: bool = False


RUNTIME_STATE = RuntimeState()


def get_config() -> AppConfig:
    if RUNTIME_STATE.config is None:
        RUNTIME_STATE.config = load_config()
    return RUNTIME_STATE.config


def initialize_runtime() -> AppContainer:
    if RUNTIME_STATE.container is None:
        RUNTIME_STATE.container = build_container(config=get_config())
    if not RUNTIME_STATE.is_registered:
        atexit.register(shutdown_runtime)
        RUNTIME_STATE.is_registered = True
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

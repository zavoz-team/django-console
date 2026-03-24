from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.observability.factory import build_observability
from adapter.observability.runtime import ObservabilityRuntime
from domain.user import User
from repository.user import InMemoryUserRepository
from usecase.user import GetUser


@dataclass(frozen=True, slots=True)
class AppRepositories:
    user: InMemoryUserRepository


@dataclass(frozen=True, slots=True)
class AppUsecases:
    get_user: GetUser


@dataclass(slots=True)
class AppContainer:
    config: AppConfig
    observability: ObservabilityRuntime
    repositories: AppRepositories
    usecases: AppUsecases
    _is_shutdown: bool = field(default=False, init=False, repr=False)

    def shutdown(self) -> None:
        if self._is_shutdown:
            return

        try:
            self.observability.shutdown()
        finally:
            self._is_shutdown = True


def build_container(
    config_path: Path | str | None = None,
    env_path: Path | str | None = None,
    environ: Mapping[str, str] | None = None,
    config: AppConfig | None = None,
) -> AppContainer:
    app_config = config
    if app_config is None:
        app_config = load_config(
            config_path=config_path,
            env_path=env_path,
            environ=environ,
        )

    observability = build_observability(app_config)

    user_repository = InMemoryUserRepository(
        observability.tracer, [User(id='123', email='aza@gglamer.ru', name='gglamer')]
    )
    repositories = AppRepositories(user=user_repository)
    usecases = AppUsecases(
        get_user=GetUser(
            repository=user_repository,
            logger=observability.logger,
            tracer=observability.tracer,
        )
    )

    return AppContainer(
        config=app_config,
        observability=observability,
        repositories=repositories,
        usecases=usecases,
    )

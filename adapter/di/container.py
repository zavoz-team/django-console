from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.observability.factory import build_observability
from adapter.observability.runtime import ObservabilityRuntime
from repository.django.audit_log import DjangoAuditLogRepository
from repository.django.user import DjangoUserRepository
from usecase.audit import ListAuditEntries, LogCriticalPageView, LogOperatorAction
from usecase.interface import AuditLogRepository, UserRepository
from usecase.user import GetUser


@dataclass(frozen=True, slots=True)
class AppRepositories:
    user: UserRepository
    audit_log: AuditLogRepository


@dataclass(frozen=True, slots=True)
class AppUsecases:
    get_user: GetUser
    log_operator_action: LogOperatorAction
    log_critical_page_view: LogCriticalPageView
    list_audit_entries: ListAuditEntries


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

    user_repository = DjangoUserRepository(observability.tracer)
    audit_log_repository = DjangoAuditLogRepository(observability.tracer)
    repositories = AppRepositories(
        user=user_repository,
        audit_log=audit_log_repository,
    )
    log_operator_action = LogOperatorAction(
        repository=audit_log_repository,
        logger=observability.logger,
        tracer=observability.tracer,
    )
    usecases = AppUsecases(
        get_user=GetUser(
            repository=user_repository,
            logger=observability.logger,
            tracer=observability.tracer,
        ),
        log_operator_action=log_operator_action,
        log_critical_page_view=LogCriticalPageView(log_operator_action),
        list_audit_entries=ListAuditEntries(
            repository=audit_log_repository,
            tracer=observability.tracer,
        ),
    )

    return AppContainer(
        config=app_config,
        observability=observability,
        repositories=repositories,
        usecases=usecases,
    )

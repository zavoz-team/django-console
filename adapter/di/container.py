from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.observability.factory import build_observability
from adapter.observability.runtime import ObservabilityRuntime
from repository.core_api.client import CoreApiClient
from repository.core_api.export import CoreApiExportGateway
from repository.core_api.profile import CoreApiProfileGateway
from repository.core_api.segment import CoreApiSegmentGateway
from repository.core_api.system import CoreApiSystemGateway
from repository.django.audit_log import DjangoAuditLogRepository
from repository.django.user import DjangoUserRepository
from usecase.audit import (
    ListAuditEntries,
    LogCriticalPageView,
    LogOperatorAction,
)
from usecase.export_job import ListJobs, TriggerExport
from usecase.interface import (
    AuditLogRepository,
    ExportGateway,
    ProfileGateway,
    SegmentGateway,
    SystemGateway,
    UserRepository,
)
from usecase.profile import GetProfile, ListProfiles
from usecase.segment import GetSegmentMembers, ListSegments


@dataclass(frozen=True, slots=True)
class AppRepositories:
    user: UserRepository
    audit_log: AuditLogRepository


@dataclass(frozen=True, slots=True)
class AppGateways:
    profile: ProfileGateway
    segment: SegmentGateway
    export: ExportGateway
    system: SystemGateway


@dataclass(frozen=True, slots=True)
class AppUsecases:
    list_profiles: ListProfiles
    get_profile: GetProfile
    list_segments: ListSegments
    get_segment_members: GetSegmentMembers
    trigger_export: TriggerExport
    list_jobs: ListJobs
    log_operator_action: LogOperatorAction
    log_critical_page_view: LogCriticalPageView
    list_audit_entries: ListAuditEntries


@dataclass(slots=True)
class AppContainer:
    config: AppConfig
    observability: ObservabilityRuntime
    core_api_client: CoreApiClient
    repositories: AppRepositories
    gateways: AppGateways
    usecases: AppUsecases
    _is_shutdown: bool = field(default=False, init=False, repr=False)

    def shutdown(self) -> None:
        if self._is_shutdown:
            return

        try:
            self.core_api_client.shutdown()
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

    core_api_client = CoreApiClient(
        config=app_config.core_api, tracer=observability.tracer
    )

    user_repository = DjangoUserRepository(tracer=observability.tracer)
    audit_log_repository = DjangoAuditLogRepository(tracer=observability.tracer)

    repositories = AppRepositories(
        user=user_repository,
        audit_log=audit_log_repository,
    )

    gateways = AppGateways(
        profile=CoreApiProfileGateway(client=core_api_client),
        segment=CoreApiSegmentGateway(client=core_api_client),
        export=CoreApiExportGateway(client=core_api_client),
        system=CoreApiSystemGateway(client=core_api_client),
    )

    log_operator_action = LogOperatorAction(
        repository=audit_log_repository,
        logger=observability.logger,
        tracer=observability.tracer,
    )

    usecases = AppUsecases(
        list_profiles=ListProfiles(
            gateway=gateways.profile,
            tracer=observability.tracer,
        ),
        get_profile=GetProfile(
            gateway=gateways.profile,
            logger=observability.logger,
            tracer=observability.tracer,
        ),
        list_segments=ListSegments(
            gateway=gateways.segment,
            tracer=observability.tracer,
        ),
        get_segment_members=GetSegmentMembers(
            gateway=gateways.segment,
            tracer=observability.tracer,
        ),
        trigger_export=TriggerExport(
            gateway=gateways.export,
            audit_log_repository=audit_log_repository,
            logger=observability.logger,
            tracer=observability.tracer,
        ),
        list_jobs=ListJobs(
            gateway=gateways.export,
            tracer=observability.tracer,
        ),
        log_operator_action=log_operator_action,
        log_critical_page_view=LogCriticalPageView(
            log_operator_action=log_operator_action
        ),
        list_audit_entries=ListAuditEntries(
            repository=audit_log_repository,
            tracer=observability.tracer,
        ),
    )

    return AppContainer(
        config=app_config,
        observability=observability,
        core_api_client=core_api_client,
        repositories=repositories,
        gateways=gateways,
        usecases=usecases,
    )

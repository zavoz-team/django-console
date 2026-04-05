from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.observability.factory import build_observability
from adapter.observability.runtime import ObservabilityRuntime
from repository.core_api.client import CoreApiClient
from repository.core_api.export import CoreApiExportGateway
from repository.core_api.mock_client import MockCoreApiClient
from repository.core_api.profile import CoreApiProfileGateway
from repository.core_api.segment import CoreApiSegmentGateway
from repository.core_api.system import CoreApiSystemGateway
from repository.django.audit_log import DjangoAuditLogRepository
from repository.django.user import DjangoUserRepository
from usecase.audit import ListAuditEntries, LogCriticalPageView, LogOperatorAction
from usecase.export_job import ListJobs, TriggerExport
from usecase.interface import (
    AuditLogRepository,
    CoreApiClientInterface,
    ExportGateway,
    ProfileGateway,
    SegmentGateway,
    SystemGateway,
    UserRepository,
)
from usecase.profile import GetProfile, ListProfiles
from usecase.segment import GetSegmentMembers, ListSegments
from usecase.user import GetUser


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
    get_user: GetUser
    get_profile: GetProfile
    list_profiles: ListProfiles
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
    core_api_client: CoreApiClientInterface
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


def _build_core_api_client(
    config: AppConfig,
    tracer,
) -> CoreApiClientInterface:
    if config.app.env == 'mock':
        client = MockCoreApiClient()
        _seed_mock_client(client)
        return client
    return CoreApiClient(config=config.core_api, tracer=tracer)


def _seed_mock_client(client: MockCoreApiClient) -> None:
    client.profiles = [
        {
            'id': 'cust-1',
            'email': 'alex@example.com',
            'name': 'Alex Stone',
            'created_at': '2026-01-10T10:00:00',
            'updated_at': '2026-02-10T11:30:00',
            'status': 'active',
            'custom_fields': {
                'external_id': 'ext-100',
                'segment': 'vip',
                'segment_id': 'seg-1',
            },
        },
        {
            'id': 'cust-2',
            'email': 'maria@example.com',
            'name': 'Maria Fox',
            'created_at': '2026-01-11T12:00:00',
            'updated_at': '2026-02-11T09:15:00',
            'status': 'active',
            'custom_fields': {
                'external_id': 'ext-101',
                'segment': 'trial',
                'segment_id': 'seg-2',
            },
        },
    ]
    client.segments = [
        {
            'id': 'seg-1',
            'name': 'VIP',
            'status': 'active',
            'created_at': '2026-01-01T08:00:00',
        },
        {
            'id': 'seg-2',
            'name': 'Trial',
            'status': 'active',
            'created_at': '2026-01-05T08:00:00',
        },
    ]
    client.jobs = [
        {
            'id': 'job-1',
            'segment_id': 'seg-1',
            'status': 'done',
            'created_at': '2026-02-12T10:00:00',
            'updated_at': '2026-02-12T10:05:00',
            'completed_at': '2026-02-12T10:05:00',
        },
        {
            'id': 'job-2',
            'segment_id': 'seg-2',
            'status': 'running',
            'created_at': '2026-02-13T14:00:00',
            'updated_at': '2026-02-13T14:10:00',
            'completed_at': None,
        },
    ]


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
    core_api_client = _build_core_api_client(
        config=app_config,
        tracer=observability.tracer,
    )

    profile_gateway = CoreApiProfileGateway(client=core_api_client)
    segment_gateway = CoreApiSegmentGateway(client=core_api_client)
    export_gateway = CoreApiExportGateway(client=core_api_client)
    gateways = AppGateways(
        profile=profile_gateway,
        segment=segment_gateway,
        export=export_gateway,
        system=CoreApiSystemGateway(client=core_api_client),
    )

    user_repository = DjangoUserRepository(tracer=observability.tracer)
    audit_log_repository = DjangoAuditLogRepository(tracer=observability.tracer)

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
        get_profile=GetProfile(
            gateway=profile_gateway,
            logger=observability.logger,
            tracer=observability.tracer,
        ),
        list_profiles=ListProfiles(
            gateway=profile_gateway,
            tracer=observability.tracer,
        ),
        list_segments=ListSegments(
            gateway=segment_gateway,
            tracer=observability.tracer,
        ),
        get_segment_members=GetSegmentMembers(
            gateway=segment_gateway,
            tracer=observability.tracer,
        ),
        trigger_export=TriggerExport(
            gateway=export_gateway,
            audit_log_repository=audit_log_repository,
            logger=observability.logger,
            tracer=observability.tracer,
        ),
        list_jobs=ListJobs(
            gateway=export_gateway,
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
        core_api_client=core_api_client,
        repositories=repositories,
        gateways=gateways,
        usecases=usecases,
    )

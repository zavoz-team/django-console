from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.observability.factory import build_observability
from adapter.observability.runtime import ObservabilityRuntime
from repository.core_api.audit import CoreApiAuditGateway
from repository.core_api.client import CoreApiClient
from repository.core_api.export import CoreApiExportGateway
from repository.core_api.job import CoreApiJobGateway
from repository.core_api.profile import CoreApiProfileGateway
from repository.core_api.segment import CoreApiSegmentGateway
from repository.core_api.system_status import CoreApiSystemStatusGateway
from usecase.interface import (
    AuditGateway,
    ExportGateway,
    JobGateway,
    ProfileGateway,
    SegmentGateway,
    SystemStatusGateway,
)


@dataclass(frozen=True, slots=True)
class AppGateways:
    profile: ProfileGateway
    segment: SegmentGateway
    export: ExportGateway
    job: JobGateway
    system_status: SystemStatusGateway
    audit: AuditGateway


@dataclass(frozen=True, slots=True)
class AppUsecases:
    pass


@dataclass(slots=True)
class AppContainer:
    config: AppConfig
    observability: ObservabilityRuntime
    core_api_client: CoreApiClient
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

    core_api_client = CoreApiClient(config=app_config.core_api)

    gateways = AppGateways(
        profile=CoreApiProfileGateway(client=core_api_client),
        segment=CoreApiSegmentGateway(client=core_api_client),
        export=CoreApiExportGateway(client=core_api_client),
        job=CoreApiJobGateway(client=core_api_client),
        system_status=CoreApiSystemStatusGateway(client=core_api_client),
        audit=CoreApiAuditGateway(client=core_api_client),
    )

    usecases = AppUsecases()

    return AppContainer(
        config=app_config,
        observability=observability,
        core_api_client=core_api_client,
        gateways=gateways,
        usecases=usecases,
    )

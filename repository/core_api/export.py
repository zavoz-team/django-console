from datetime import datetime

from domain.export_job import ExportJob, ExportJobStatus
from repository.core_api.dto import CoreApiExportJobDTO
from repository.core_api.errors import CoreApiDataError
from usecase.interface import CoreApiClientInterface


def _to_domain_export_job(dto: CoreApiExportJobDTO) -> ExportJob:
    try:
        return ExportJob(
            id=dto.id,
            segment_id=dto.segment_id,
            status=ExportJobStatus(dto.status),
            created_at=datetime.fromisoformat(dto.created_at),
            updated_at=datetime.fromisoformat(dto.updated_at),
            completed_at=datetime.fromisoformat(dto.completed_at) if dto.completed_at else None,
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid export job data: {exc}") from exc


class CoreApiExportGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def trigger_export(
        self, segment_id: str, actor_id: str, trace_id: str
    ) -> ExportJob:
        extra_headers = {
            "X-Actor-ID": actor_id,
            "X-Trace-ID": trace_id,
        }
        response_data = self._client.trigger_export(
            segment_id, extra_headers=extra_headers
        )
        return _to_domain_export_job(CoreApiExportJobDTO(**response_data))

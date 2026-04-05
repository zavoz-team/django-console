from datetime import datetime

from domain.export_job import ExportJobStatus, ExportJobSummary
from domain.query import Pagination
from repository.core_api.dto import CoreApiExportJobDTO
from repository.core_api.errors import CoreApiDataError
from usecase.interface import CoreApiClientInterface


def _to_domain_export_job_summary(dto: CoreApiExportJobDTO) -> ExportJobSummary:
    try:
        return ExportJobSummary(
            id=dto.id,
            status=ExportJobStatus(dto.status.lower()),
            created_at=datetime.fromisoformat(dto.created_at),
            finished_at=datetime.fromisoformat(dto.completed_at) if dto.completed_at else None,
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid export job data: {exc}") from exc


class CoreApiExportGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def trigger_export(self, segment_id: str, destination: str) -> ExportJobSummary:
        response_data = self._client.trigger_export(
            segment_id=segment_id,
            destination=destination,
        )
        return _to_domain_export_job_summary(CoreApiExportJobDTO(**response_data))

    def list_jobs(self, pagination: Pagination) -> list[ExportJobSummary]:
        jobs_data = self._client.get_jobs(
            limit=pagination.limit,
            offset=pagination.offset,
        )
        return [
            _to_domain_export_job_summary(CoreApiExportJobDTO(**item))
            for item in jobs_data
        ]

from collections.abc import Sequence

from domain.export_job import ExportJobStatus, ExportJobSummary
from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNotFoundError
from usecase.interface import JobGateway


class CoreApiJobGateway(JobGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_jobs(self, limit: int = 50, offset: int = 0) -> Sequence[ExportJobSummary]:
        response_data = self._client.get_jobs(limit=limit, offset=offset)

        jobs = []
        for item in response_data.get("items", []):
            jobs.append(
                ExportJobSummary(
                    job_id=item["job_id"],
                    segment_id=item.get("segment_id", ""),
                    status=ExportJobStatus(item["status"]),
                    requested_at=item.get("requested_at", ""),
                    completed_at=item.get("completed_at"),
                    members_count=item.get("members_count"),
                    error_reason=item.get("error_reason"),
                    requested_by=item.get("requested_by"),
                )
            )

        return jobs

    def get_job(self, job_id: str) -> ExportJobSummary | None:
        try:
            data = self._client.get_job(job_id)
            return ExportJobSummary(
                job_id=data["job_id"],
                segment_id=data.get("segment_id", ""),
                status=ExportJobStatus(data["status"]),
                requested_at=data.get("requested_at", ""),
                completed_at=data.get("completed_at"),
                members_count=data.get("members_count"),
                error_reason=data.get("error_reason"),
                requested_by=data.get("requested_by"),
            )
        except CoreApiNotFoundError:
            return None

from domain.export_job import ExportJobStatus, ExportJobSummary
from domain.query import Pagination
from repository.core_api.client import CoreApiClient
from usecase.interface import ExportGateway


class CoreApiExportGateway(ExportGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def trigger_export(
        self,
        segment_id: str,
        destination_type: str,
        destination_url: str,
        requested_by: str | None = None,
    ) -> ExportJobSummary:
        data = self._client.trigger_export(
            segment_id=segment_id,
            destination_type=destination_type,
            destination_url=destination_url,
            requested_by=requested_by,
        )
        return ExportJobSummary(
            job_id=data["job_id"],
            segment_id=data.get("segment_id", segment_id),
            status=ExportJobStatus(data["status"]),
            requested_at=data.get("requested_at", ""),
            completed_at=data.get("completed_at"),
            members_count=data.get("members_count"),
            error_reason=data.get("error_reason"),
            requested_by=None,
        )

    def list_jobs(self, pagination: Pagination) -> list[ExportJobSummary]:
        response_data = self._client.get_jobs(
            limit=pagination.limit, offset=pagination.offset
        )

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

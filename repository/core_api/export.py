from domain.export_job import ExportJobSummary
from domain.query import Pagination
from repository.core_api.client import CoreApiClient
from usecase.interface import ExportGateway


class CoreApiExportGateway(ExportGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def trigger_export(self, segment_id: str, destination: str) -> ExportJobSummary:
        response_data = self._client.trigger_export(
            segment_id=segment_id,
            destination=destination,
        )
        return ExportJobSummary(**response_data)

    def list_jobs(self, pagination: Pagination) -> list[ExportJobSummary]:
        response_data = self._client.get_jobs(
            limit=pagination.limit, offset=pagination.offset
        )

        jobs = []
        if isinstance(response_data, list):
            for item in response_data:
                jobs.append(ExportJobSummary(**item))

        return jobs

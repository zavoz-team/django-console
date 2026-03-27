from collections.abc import Sequence

from domain.export_job import ExportJobSummary
from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNotFoundError
from usecase.interface import JobGateway


class CoreApiJobGateway(JobGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_jobs(self, limit: int = 50, offset: int = 0) -> Sequence[ExportJobSummary]:
        response_data = self._client.get_jobs(limit=limit, offset=offset)

        jobs = []
        if isinstance(response_data, list):
            for item in response_data:
                jobs.append(ExportJobSummary(**item))

        return jobs

    def get_job(self, job_id: str) -> ExportJobSummary | None:
        try:
            response_data = self._client.get_job(job_id)
            return ExportJobSummary(**response_data)
        except CoreApiNotFoundError:
            return None

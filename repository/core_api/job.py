from collections.abc import Sequence

from repository.core_api.client import CoreApiClient
from repository.core_api.dto import CoreApiJobDTO
from repository.core_api.errors import CoreApiNotFoundError
from usecase.dto import JobDTO
from usecase.interface import JobGateway


def _to_job_dto(core_dto: CoreApiJobDTO) -> JobDTO:
    return JobDTO(id=core_dto.id, status=core_dto.status)


class CoreApiJobGateway(JobGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_jobs(self, limit: int = 50, offset: int = 0) -> Sequence[JobDTO]:
        response_data = self._client.get_jobs(limit=limit, offset=offset)

        jobs = []
        if isinstance(response_data, list):
            for item in response_data:
                core_dto = CoreApiJobDTO(**item)
                jobs.append(_to_job_dto(core_dto))

        return jobs

    def get_job(self, job_id: str) -> JobDTO | None:
        try:
            response_data = self._client.get_job(job_id)
            core_dto = CoreApiJobDTO(**response_data)
            return _to_job_dto(core_dto)
        except CoreApiNotFoundError:
            return None

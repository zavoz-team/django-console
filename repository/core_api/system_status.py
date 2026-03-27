from repository.core_api.client import CoreApiClient
from repository.core_api.dto import CoreApiSystemStatusDTO
from usecase.dto import SystemStatusDTO
from usecase.interface import SystemStatusGateway


def _to_system_status_dto(core_dto: CoreApiSystemStatusDTO) -> SystemStatusDTO:
    return SystemStatusDTO(status=core_dto.status)


class CoreApiSystemStatusGateway(SystemStatusGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def get_status(self) -> SystemStatusDTO:
        response_data = self._client.get_system_status()
        core_dto = CoreApiSystemStatusDTO(**response_data)
        return _to_system_status_dto(core_dto)

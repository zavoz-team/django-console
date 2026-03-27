from domain.system_status import SystemStatus
from repository.core_api.client import CoreApiClient
from usecase.interface import SystemStatusGateway


class CoreApiSystemStatusGateway(SystemStatusGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def get_status(self) -> SystemStatus:
        response_data = self._client.get_system_status()
        return SystemStatus(**response_data)

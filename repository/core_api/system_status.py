from usecase.dto import SystemStatusDTO
from usecase.interface import CoreApiClientInterface


class CoreApiSystemStatusGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def get_status(self) -> SystemStatusDTO:
        response_data = self._client.get_system_status()
        return SystemStatusDTO(**response_data)

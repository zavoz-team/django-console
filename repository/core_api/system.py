from repository.core_api.client import CoreApiClient
from usecase.interface import SystemGateway


class CoreApiSystemGateway(SystemGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def is_core_available(self) -> bool:
        try:
            self._client.get_system_status()
            return True
        except Exception:
            return False

from dataclasses import dataclass

from domain.error import CoreUnavailableError
from usecase.interface import SystemGateway, Tracer


@dataclass(frozen=True, slots=True)
class GetSystemStatusQuery:
    pass


class GetSystemStatus:
    def __init__(
        self,
        gateway: SystemGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: GetSystemStatusQuery) -> bool:
        with self._tracer.start_span('usecase.get_system_status'):
            available = self._gateway.is_core_available()
            if not available:
                raise CoreUnavailableError()
            return True

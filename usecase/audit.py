from dataclasses import dataclass

from domain.audit import AuditEntry
from domain.query import Pagination
from usecase.interface import AuditGateway, Logger, Tracer


@dataclass(frozen=True, slots=True)
class LogOperatorActionCommand:
    entry: AuditEntry


@dataclass(frozen=True, slots=True)
class ListAuditEntriesQuery:
    pagination: Pagination


class LogOperatorAction:
    def __init__(
        self,
        gateway: AuditGateway,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._logger = logger
        self._tracer = tracer

    def execute(self, command: LogOperatorActionCommand) -> None:
        raise NotImplementedError()


class ListAuditEntries:
    def __init__(
        self,
        gateway: AuditGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListAuditEntriesQuery) -> list[AuditEntry]:
        raise NotImplementedError()

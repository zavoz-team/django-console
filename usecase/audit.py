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
        with self._tracer.start_span(
            'usecase.log_operator_action',
            attrs={
                'audit.id': command.entry.id,
                'audit.action': command.entry.action,
            },
        ):
            self._gateway.log_operator_action(command.entry)
            self._logger.info(
                'operator_action_logged',
                attrs={'audit_id': command.entry.id},
            )


class ListAuditEntries:
    def __init__(
        self,
        gateway: AuditGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListAuditEntriesQuery) -> list[AuditEntry]:
        with self._tracer.start_span(
            'usecase.list_audit_entries',
            attrs={
                'pagination.limit': query.pagination.limit,
                'pagination.offset': query.pagination.offset,
            },
        ):
            return self._gateway.list_entries(query.pagination)

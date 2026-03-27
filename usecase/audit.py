from dataclasses import dataclass

from domain.audit import AuditEntry
from domain.query import Pagination
from usecase.interface import AuditLogRepository, Logger, Tracer


@dataclass(frozen=True, slots=True)
class LogOperatorActionCommand:
    entry: AuditEntry


@dataclass(frozen=True, slots=True)
class ListAuditEntriesQuery:
    pagination: Pagination
    target_type: str | None = None
    target_id: str | None = None


@dataclass(frozen=True, slots=True)
class LogCriticalPageViewCommand:
    actor_email: str
    page_name: str
    payload_json: dict[str, str | int | float | bool]
    trace_id: str | None = None


class LogOperatorAction:
    def __init__(
        self,
        repository: AuditLogRepository,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._repository = repository
        self._logger = logger
        self._tracer = tracer

    def execute(self, command: LogOperatorActionCommand) -> AuditEntry:
        with self._tracer.start_span(
            'usecase.log_operator_action',
            attrs={
                'audit.id': command.entry.id,
                'audit.action': command.entry.action,
            },
        ):
            entry = self._repository.save(command.entry)
            self._logger.info(
                'operator_action_logged',
                attrs={'audit_id': entry.id},
            )
            return entry


class ListAuditEntries:
    def __init__(
        self,
        repository: AuditLogRepository,
        tracer: Tracer,
    ) -> None:
        self._repository = repository
        self._tracer = tracer

    def execute(self, query: ListAuditEntriesQuery) -> list[AuditEntry]:
        with self._tracer.start_span(
            'usecase.list_audit_entries',
            attrs={
                'pagination.limit': query.pagination.limit,
                'pagination.offset': query.pagination.offset,
            },
        ):
            if query.target_type is not None and query.target_id is not None:
                return self._repository.list_by_target(
                    target_type=query.target_type,
                    target_id=query.target_id,
                    pagination=query.pagination,
                )
            return self._repository.list_recent(query.pagination)


class LogCriticalPageView:
    def __init__(self, log_operator_action: LogOperatorAction) -> None:
        self._log_operator_action = log_operator_action

    def execute(self, command: LogCriticalPageViewCommand) -> AuditEntry:
        return self._log_operator_action.execute(
            LogOperatorActionCommand(
                entry=AuditEntry(
                    id=0,
                    actor_email=command.actor_email,
                    action='view_critical_page',
                    target_type='page',
                    target_id=command.page_name,
                    status='success',
                    payload_json=command.payload_json,
                    trace_id=command.trace_id,
                )
            )
        )

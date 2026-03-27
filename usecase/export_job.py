from dataclasses import dataclass

from domain.audit import AuditEntry
from domain.error import ExportTriggerError
from domain.export_job import ExportJobSummary
from domain.query import Pagination
from usecase.interface import AuditLogRepository, ExportGateway, Logger, Tracer


@dataclass(frozen=True, slots=True)
class TriggerExportQuery:
    segment_id: str
    destination: str
    actor_email: str
    actor_id: str | None = None
    trace_id: str | None = None


@dataclass(frozen=True, slots=True)
class ListJobsQuery:
    pagination: Pagination


class TriggerExport:
    def __init__(
        self,
        gateway: ExportGateway,
        audit_log_repository: AuditLogRepository,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._audit_log_repository = audit_log_repository
        self._logger = logger
        self._tracer = tracer

    def execute(self, query: TriggerExportQuery) -> ExportJobSummary:
        with self._tracer.start_span(
            'usecase.trigger_export',
            attrs={
                'segment.id': query.segment_id,
                'export.destination': query.destination,
            },
        ) as span:
            try:
                job = self._gateway.trigger_export(
                    segment_id=query.segment_id,
                    destination=query.destination,
                )
            except Exception as exc:
                self._audit_log_repository.save(
                    AuditEntry(
                        id=0,
                        actor_email=query.actor_email,
                        action='trigger_export',
                        target_type='segment',
                        target_id=query.segment_id,
                        status='failed',
                        payload_json={
                            'destination': query.destination,
                            'actor_id': query.actor_id or '',
                            'error': str(exc),
                        },
                        trace_id=query.trace_id,
                    )
                )
                error = ExportTriggerError(reason=str(exc))
                span.record_error(error)
                self._logger.error(
                    'export_trigger_error',
                    attrs={'segment_id': query.segment_id},
                )
                raise error from exc

            self._audit_log_repository.save(
                AuditEntry(
                    id=0,
                    actor_email=query.actor_email,
                    action='trigger_export',
                    target_type='segment',
                    target_id=query.segment_id,
                    status='success',
                    payload_json={
                        'destination': query.destination,
                        'actor_id': query.actor_id or '',
                        'export_job_id': job.id,
                    },
                    trace_id=query.trace_id,
                )
            )
            span.set_attribute('export_job.id', job.id)
            return job


class ListJobs:
    def __init__(
        self,
        gateway: ExportGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListJobsQuery) -> list[ExportJobSummary]:
        with self._tracer.start_span(
            'usecase.list_jobs',
            attrs={
                'pagination.limit': query.pagination.limit,
                'pagination.offset': query.pagination.offset,
            },
        ):
            return self._gateway.list_jobs(query.pagination)

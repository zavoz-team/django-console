from dataclasses import dataclass

from domain.error import ExportTriggerError
from domain.export_job import ExportJobSummary
from domain.query import Pagination
from usecase.interface import ExportGateway, Logger, Tracer


@dataclass(frozen=True, slots=True)
class TriggerExportQuery:
    segment_id: str


@dataclass(frozen=True, slots=True)
class ListJobsQuery:
    pagination: Pagination


class TriggerExport:
    def __init__(
        self,
        gateway: ExportGateway,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._logger = logger
        self._tracer = tracer

    def execute(self, query: TriggerExportQuery) -> ExportJobSummary:
        with self._tracer.start_span(
            'usecase.trigger_export',
            attrs={'segment.id': query.segment_id},
        ) as span:
            try:
                job = self._gateway.trigger(query.segment_id)
            except Exception as exc:
                error = ExportTriggerError(reason=str(exc))
                span.record_error(error)
                self._logger.error(
                    'export_trigger_error',
                    attrs={'segment_id': query.segment_id},
                )
                raise error from exc

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

from dataclasses import dataclass

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
        raise NotImplementedError()


class ListJobs:
    def __init__(
        self,
        gateway: ExportGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListJobsQuery) -> list[ExportJobSummary]:
        raise NotImplementedError()

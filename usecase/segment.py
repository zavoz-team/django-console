from dataclasses import dataclass

from domain.query import Pagination
from domain.segment import SegmentMember, SegmentSummary
from usecase.interface import SegmentGateway, Tracer


@dataclass(frozen=True, slots=True)
class ListSegmentsQuery:
    pagination: Pagination


@dataclass(frozen=True, slots=True)
class GetSegmentMembersQuery:
    segment_id: str
    pagination: Pagination


class ListSegments:
    def __init__(
        self,
        gateway: SegmentGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListSegmentsQuery) -> list[SegmentSummary]:
        raise NotImplementedError()


class GetSegmentMembers:
    def __init__(
        self,
        gateway: SegmentGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: GetSegmentMembersQuery) -> list[SegmentMember]:
        raise NotImplementedError()

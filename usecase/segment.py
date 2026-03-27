from dataclasses import dataclass

from domain.error import SegmentNotFoundError
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
        with self._tracer.start_span(
            'usecase.list_segments',
            attrs={
                'pagination.limit': query.pagination.limit,
                'pagination.offset': query.pagination.offset,
            },
        ):
            return self._gateway.list_segments(query.pagination)


class GetSegmentMembers:
    def __init__(
        self,
        gateway: SegmentGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: GetSegmentMembersQuery) -> list[SegmentMember]:
        with self._tracer.start_span(
            'usecase.get_segment_members',
            attrs={
                'segment.id': query.segment_id,
                'pagination.limit': query.pagination.limit,
                'pagination.offset': query.pagination.offset,
            },
        ):
            members = self._gateway.list_members(
                segment_id=query.segment_id,
                pagination=query.pagination,
            )
            if members is None:
                raise SegmentNotFoundError(query.segment_id)
            return members

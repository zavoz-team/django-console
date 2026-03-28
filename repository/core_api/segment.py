from domain.query import Pagination
from domain.segment import SegmentMember, SegmentSummary
from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNotFoundError
from usecase.interface import SegmentGateway


class CoreApiSegmentGateway(SegmentGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_segments(self, pagination: Pagination) -> list[SegmentSummary]:
        response_data = self._client.get_segments(
            limit=pagination.limit, offset=pagination.offset
        )

        segments = []
        if isinstance(response_data, list):
            for item in response_data:
                segments.append(SegmentSummary(**item))

        return segments

    def list_members(
        self, segment_id: str, pagination: Pagination
    ) -> list[SegmentMember] | None:
        try:
            response_data = self._client.get_segment_members(
                segment_id=segment_id, limit=pagination.limit, offset=pagination.offset
            )
        except CoreApiNotFoundError:
            return None

        members = []
        if isinstance(response_data, list):
            for item in response_data:
                members.append(SegmentMember(**item))

        return members

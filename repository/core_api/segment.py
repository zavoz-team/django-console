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
        for item in response_data.get("items", []):
            segments.append(
                SegmentSummary(
                    segment_id=item["segment_id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    is_active=item.get("is_active", True),
                    members_count=item.get("members_count"),
                )
            )

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

        resolved_segment_id = response_data.get("segment_id", segment_id)
        members = []
        for item in response_data.get("items", []):
            members.append(
                SegmentMember(
                    segment_id=resolved_segment_id,
                    customer_id=item["customer_id"],
                    email=item.get("email"),
                    phone=item.get("phone"),
                    external_user_id=item.get("external_user_id"),
                )
            )

        return members

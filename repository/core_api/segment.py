from datetime import datetime

from domain.segment import SegmentMember, SegmentSummary
from repository.core_api.dto import CoreApiProfileDTO, CoreApiSegmentDTO
from repository.core_api.errors import CoreApiDataError, CoreApiNotFoundError
from usecase.interface import CoreApiClientInterface


def _to_segment_summary(dto: CoreApiSegmentDTO) -> SegmentSummary:
    try:
        return SegmentSummary(
            id=dto.id,
            name=dto.name,
            updated_at=datetime.fromisoformat(dto.created_at),
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid segment data: {exc}") from exc


def _to_segment_member(dto: CoreApiProfileDTO, segment_id: str) -> SegmentMember:
    return SegmentMember(
        segment_id=segment_id,
        profile_id=dto.id,
    )


class CoreApiSegmentGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def list_segments(self, pagination) -> list[SegmentSummary]:
        segments_data = self._client.get_segments(
            limit=pagination.limit,
            offset=pagination.offset,
        )
        return [_to_segment_summary(CoreApiSegmentDTO(**item)) for item in segments_data]

    def list_members(self, segment_id: str, pagination) -> list[SegmentMember] | None:
        try:
            members_data = self._client.get_segment_members(
                segment_id=segment_id,
                limit=pagination.limit,
                offset=pagination.offset,
            )
        except CoreApiNotFoundError:
            return None
        return [
            _to_segment_member(CoreApiProfileDTO(**item), segment_id)
            for item in members_data
        ]

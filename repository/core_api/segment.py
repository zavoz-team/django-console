from collections.abc import Sequence
from datetime import datetime

from domain.profile import ProfileSummary
from domain.segment import SegmentSummary
from repository.core_api.dto import CoreApiProfileDTO, CoreApiSegmentDTO
from repository.core_api.errors import CoreApiDataError
from repository.core_api.profile import _to_profile_summary
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


class CoreApiSegmentGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def list_segments(self, limit: int = 50, offset: int = 0) -> Sequence[SegmentSummary]:
        segments_data = self._client.get_segments(limit=limit, offset=offset)
        return [_to_segment_summary(CoreApiSegmentDTO(**item)) for item in segments_data]

    def get_segment_members(
        self, segment_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[ProfileSummary]:
        members_data = self._client.get_segment_members(
            segment_id=segment_id, limit=limit, offset=offset
        )
        return [_to_profile_summary(CoreApiProfileDTO(**item)) for item in members_data]

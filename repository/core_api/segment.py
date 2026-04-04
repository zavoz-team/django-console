from collections.abc import Sequence
from datetime import datetime

from domain.profile import Profile
from domain.segment import Segment, SegmentStatus
from repository.core_api.dto import CoreApiProfileDTO, CoreApiSegmentDTO
from repository.core_api.errors import CoreApiDataError
from repository.core_api.profile import _to_domain_profile
from usecase.interface import CoreApiClientInterface


def _to_domain_segment(dto: CoreApiSegmentDTO) -> Segment:
    try:
        return Segment(
            id=dto.id,
            name=dto.name,
            status=SegmentStatus(dto.status),
            created_at=datetime.fromisoformat(dto.created_at),
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid segment data: {exc}") from exc


class CoreApiSegmentGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def list_segments(self, limit: int = 50, offset: int = 0) -> Sequence[Segment]:
        response_data = self._client.get_segments(limit=limit, offset=offset)
        segments_data = response_data.get("segments", [])
        if not isinstance(segments_data, list):
            raise CoreApiDataError("Invalid segments list format")

        return [_to_domain_segment(CoreApiSegmentDTO(**item)) for item in segments_data]

    def get_segment_members(
        self, segment_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[Profile]:
        response_data = self._client.get_segment_members(
            segment_id=segment_id, limit=limit, offset=offset
        )
        members_data = response_data.get("members", [])
        if not isinstance(members_data, list):
            raise CoreApiDataError("Invalid segment members list format")

        return [_to_domain_profile(CoreApiProfileDTO(**item)) for item in members_data]

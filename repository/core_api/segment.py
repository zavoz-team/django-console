from collections.abc import Sequence

from repository.core_api.client import CoreApiClient
from repository.core_api.dto import CoreApiProfileDTO, CoreApiSegmentDTO
from usecase.dto import ProfileDTO, SegmentDTO
from usecase.interface import SegmentGateway


def _to_segment_dto(core_dto: CoreApiSegmentDTO) -> SegmentDTO:
    return SegmentDTO(id=core_dto.id, name=core_dto.name)


def _to_profile_dto(core_dto: CoreApiProfileDTO) -> ProfileDTO:
    return ProfileDTO(id=core_dto.id, name=core_dto.name)


class CoreApiSegmentGateway(SegmentGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_segments(self, limit: int = 50, offset: int = 0) -> Sequence[SegmentDTO]:
        response_data = self._client.get_segments(limit=limit, offset=offset)

        segments = []
        if isinstance(response_data, list):
            for item in response_data:
                core_dto = CoreApiSegmentDTO(**item)
                segments.append(_to_segment_dto(core_dto))

        return segments

    def get_segment_members(
        self, segment_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[ProfileDTO]:
        response_data = self._client.get_segment_members(
            segment_id=segment_id, limit=limit, offset=offset
        )

        members = []
        if isinstance(response_data, list):
            for item in response_data:
                core_dto = CoreApiProfileDTO(**item)
                members.append(_to_profile_dto(core_dto))

        return members

from collections.abc import Sequence

from repository.core_api.client import CoreApiClient
from repository.core_api.dto import CoreApiProfileDTO
from repository.core_api.errors import CoreApiNotFoundError
from usecase.dto import ProfileDTO
from usecase.interface import ProfileGateway


def _to_profile_dto(core_dto: CoreApiProfileDTO) -> ProfileDTO:
    return ProfileDTO(id=core_dto.id, name=core_dto.name)


class CoreApiProfileGateway(ProfileGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_profiles(self, limit: int = 50, offset: int = 0) -> Sequence[ProfileDTO]:
        response_data = self._client.get_profiles(limit=limit, offset=offset)
        
        profiles = []
        if isinstance(response_data, list):
            for item in response_data:
                core_dto = CoreApiProfileDTO(**item)
                profiles.append(_to_profile_dto(core_dto))
        
        return profiles

    def get_profile(self, customer_id: str) -> ProfileDTO | None:
        try:
            response_data = self._client.get_profile(customer_id)
            core_dto = CoreApiProfileDTO(**response_data)
            return _to_profile_dto(core_dto)
        except CoreApiNotFoundError:
            return None

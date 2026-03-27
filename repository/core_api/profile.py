from collections.abc import Sequence

from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNotFoundError
from usecase.dto import ProfileDTO
from usecase.interface import ProfileGateway


class CoreApiProfileGateway(ProfileGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list_profiles(self, limit: int = 50, offset: int = 0) -> Sequence[ProfileDTO]:
        response_data = self._client.get_profiles(limit=limit, offset=offset)

        profiles = []
        if isinstance(response_data, list):
            for item in response_data:
                profiles.append(ProfileDTO(**item))

        return profiles

    def get_profile(self, customer_id: str) -> ProfileDTO | None:
        try:
            response_data = self._client.get_profile(customer_id)
            return ProfileDTO(**response_data)
        except CoreApiNotFoundError:
            return None

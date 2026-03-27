from domain.profile import ProfileDetails, ProfileSummary
from domain.query import Pagination, TextQuery
from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNotFoundError
from usecase.interface import ProfileGateway


class CoreApiProfileGateway(ProfileGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list(
        self, pagination: Pagination, query: TextQuery | None = None
    ) -> list[ProfileSummary]:
        response_data = self._client.get_profiles(
            limit=pagination.limit, offset=pagination.offset
        )

        profiles = []
        if isinstance(response_data, list):
            for item in response_data:
                profiles.append(ProfileSummary(**item))

        return profiles

    def get(self, profile_id: str) -> ProfileDetails | None:
        try:
            response_data = self._client.get_profile(profile_id)
            return ProfileDetails(**response_data)
        except CoreApiNotFoundError:
            return None

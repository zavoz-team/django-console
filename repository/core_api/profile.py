from collections.abc import Sequence
from datetime import datetime

from domain.profile import ProfileDetails, ProfileSummary
from domain.query import Pagination, TextQuery
from repository.core_api.dto import CoreApiProfileDTO
from repository.core_api.errors import CoreApiDataError, CoreApiNotFoundError
from usecase.interface import CoreApiClientInterface


def _to_profile_summary(dto: CoreApiProfileDTO) -> ProfileSummary:
    try:
        return ProfileSummary(
            id=dto.id,
            display_name=dto.name,
            email=dto.email,
            updated_at=datetime.fromisoformat(dto.updated_at),
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid profile data: {exc}") from exc


def _to_profile_details(dto: CoreApiProfileDTO) -> ProfileDetails:
    try:
        return ProfileDetails(
            id=dto.id,
            display_name=dto.name,
            email=dto.email,
            updated_at=datetime.fromisoformat(dto.updated_at),
            attributes=dto.custom_fields,
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid profile data: {exc}") from exc


class CoreApiProfileGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def list_profiles(
        self, pagination: Pagination, query: TextQuery | None = None
    ) -> Sequence[ProfileSummary]:
        profiles_data = self._client.get_profiles(
            limit=pagination.limit,
            offset=pagination.offset,
            query=query,
        )
        return [_to_profile_summary(CoreApiProfileDTO(**item)) for item in profiles_data]

    def get_profile(self, customer_id: str) -> ProfileDetails | None:
        try:
            response_data = self._client.get_profile(customer_id)
            if not response_data:
                return None
            return _to_profile_details(CoreApiProfileDTO(**response_data))
        except CoreApiNotFoundError:
            return None

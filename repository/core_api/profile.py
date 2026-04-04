from collections.abc import Sequence
from datetime import datetime

from domain.profile import Profile, ProfileStatus
from domain.query import Pagination, TextQuery
from repository.core_api.dto import CoreApiProfileDTO
from repository.core_api.errors import CoreApiDataError, CoreApiNotFoundError
from usecase.interface import CoreApiClientInterface


def _to_domain_profile(dto: CoreApiProfileDTO) -> Profile:
    try:
        return Profile(
            id=dto.id,
            email=dto.email,
            name=dto.name,
            created_at=datetime.fromisoformat(dto.created_at),
            updated_at=datetime.fromisoformat(dto.updated_at),
            status=ProfileStatus(dto.status),
            custom_fields=dto.custom_fields,
        )
    except (ValueError, TypeError) as exc:
        raise CoreApiDataError(f"Invalid profile data: {exc}") from exc


class CoreApiProfileGateway:
    def __init__(self, client: CoreApiClientInterface) -> None:
        self._client = client

    def list_profiles(
        self, pagination: Pagination, query: TextQuery | None = None
    ) -> Sequence[Profile]:
        profiles_data = self._client.get_profiles(
            limit=pagination.limit,
            offset=pagination.offset,
            query=query,
        )
        return [_to_domain_profile(CoreApiProfileDTO(**item)) for item in profiles_data]

    def get_profile(self, customer_id: str) -> Profile | None:
        try:
            response_data = self._client.get_profile(customer_id)
            if not response_data:
                return None
            return _to_domain_profile(CoreApiProfileDTO(**response_data))
        except CoreApiNotFoundError:
            return None

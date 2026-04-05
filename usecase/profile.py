from dataclasses import dataclass

from domain.error import CoreUnavailableError, ProfileNotFoundError
from domain.profile import ProfileDetails, ProfileSummary
from domain.query import Pagination, TextQuery
from usecase.interface import Logger, ProfileGateway, Tracer


@dataclass(frozen=True, slots=True)
class GetProfileQuery:
    profile_id: str


@dataclass(frozen=True, slots=True)
class ListProfilesQuery:
    pagination: Pagination
    query: TextQuery | None = None


class GetProfile:
    def __init__(
        self,
        gateway: ProfileGateway,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._logger = logger
        self._tracer = tracer

    def execute(self, query: GetProfileQuery) -> ProfileDetails:
        with self._tracer.start_span(
            'usecase.get_profile',
            attrs={'profile.id': query.profile_id},
        ) as span:
            try:
                profile = self._gateway.get_profile(query.profile_id)
            except Exception as exc:
                error = CoreUnavailableError()
                span.record_error(exc)
                self._logger.error(
                    'core_unavailable',
                    attrs={'profile_id': query.profile_id},
                )
                raise error from exc
            if profile is None:
                error = ProfileNotFoundError(query.profile_id)
                span.record_error(error)
                self._logger.warning(
                    'profile_not_found',
                    attrs={'profile_id': query.profile_id},
                )
                raise error

            return profile


class ListProfiles:
    def __init__(
        self,
        gateway: ProfileGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListProfilesQuery) -> list[ProfileSummary]:
        with self._tracer.start_span(
            'usecase.list_profiles',
            attrs={
                'pagination.limit': query.pagination.limit,
                'pagination.offset': query.pagination.offset,
                'query': query.query.value if query.query else '',
            },
        ) as span:
            try:
                return self._gateway.list_profiles(
                    pagination=query.pagination,
                    query=query.query,
                )
            except Exception as exc:
                span.record_error(exc)
                raise CoreUnavailableError() from exc

from dataclasses import dataclass

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
        raise NotImplementedError()


class ListProfiles:
    def __init__(
        self,
        gateway: ProfileGateway,
        tracer: Tracer,
    ) -> None:
        self._gateway = gateway
        self._tracer = tracer

    def execute(self, query: ListProfilesQuery) -> list[ProfileSummary]:
        raise NotImplementedError()

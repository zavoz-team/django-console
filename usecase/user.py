from dataclasses import dataclass

from domain.error import UserNotFoundError
from domain.user import User
from usecase.interface import Logger, Tracer, UserRepository


@dataclass(frozen=True, slots=True)
class GetUserQuery:
    user_id: str


class GetUser:
    def __init__(
        self,
        repository: UserRepository,
        logger: Logger,
        tracer: Tracer,
    ) -> None:
        self._repository = repository
        self._logger = logger
        self._tracer = tracer

    def execute(self, query: GetUserQuery) -> User:
        with self._tracer.start_span(
            'usecase.get_user',
            attrs={'user.id': query.user_id},
        ) as span:
            user = self._repository.get(query.user_id)
            if user is None:
                error = UserNotFoundError(query.user_id)
                span.record_error(error)
                self._logger.warning(
                    'user_not_found',
                    attrs={'user_id': query.user_id},
                )
                raise error

            span.set_attribute('user.email', user.email)
            self._logger.info('user_loaded', attrs={'user_id': user.id})
            return user

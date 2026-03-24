from collections.abc import Iterable

from domain.user import User
from usecase.interface import Tracer, UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(
        self,
        tracer: Tracer,
        users: Iterable[User] | None = None,
    ) -> None:
        self._users = {user.id: user for user in users or ()}
        self._tracer = tracer

    def get(self, user_id: str) -> User | None:
        with self._tracer.start_span('repository.user', attrs={'user.id': user_id}):
            return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def save(self, user: User) -> None:
        self._users[user.id] = user

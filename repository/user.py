from collections.abc import Iterable

from domain.user import User
from usecase.interface import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self, users: Iterable[User] | None = None) -> None:
        self._users = {user.id: user for user in users or ()}

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def save(self, user: User) -> None:
        self._users[user.id] = user

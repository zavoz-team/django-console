from domain.user import User
from repository.django.models import UserRecord


def to_domain(record: UserRecord) -> User:
    return User(id=record.id, email=record.email, name=record.name)


def to_record_data(user: User) -> dict[str, str]:
    return {'email': user.email, 'name': user.name}

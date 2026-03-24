from domain.user import User
from repository.django.dto import to_domain, to_record_data
from repository.django.models import UserRecord
from usecase.interface import Tracer, UserRepository


class DjangoUserRepository(UserRepository):
    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def get(self, user_id: str) -> User | None:
        with self._tracer.start_span('repository.user', attrs={'user.id': user_id}):
            record = UserRecord.objects.filter(id=user_id).first()
            if record is None:
                return None
            return to_domain(record)

    def get_by_email(self, email: str) -> User | None:
        with self._tracer.start_span(
            'repository.user.get_by_email',
            attrs={'user.email': email},
        ):
            record = UserRecord.objects.filter(email=email).first()
            if record is None:
                return None
            return to_domain(record)

    def save(self, user: User) -> None:
        with self._tracer.start_span(
            'repository.user.save',
            attrs={'user.id': user.id, 'user.email': user.email},
        ):
            UserRecord.objects.update_or_create(
                id=user.id,
                defaults=to_record_data(user),
            )

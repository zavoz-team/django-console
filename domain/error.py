class DomainError(Exception):
    pass


class UserError(DomainError):
    pass


class UserNotFoundError(UserError):
    def __init__(self, user_id: str) -> None:
        super().__init__('user_not_found')
        self.user_id = user_id


class UserConflictError(UserError):
    def __init__(self, email: str) -> None:
        super().__init__('user_conflict')
        self.email = email

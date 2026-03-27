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


class ProfileError(DomainError):
    pass


class ProfileNotFoundError(ProfileError):
    def __init__(self, profile_id: str) -> None:
        super().__init__('profile_not_found')
        self.profile_id = profile_id


class SegmentError(DomainError):
    pass


class SegmentNotFoundError(SegmentError):
    def __init__(self, segment_id: str) -> None:
        super().__init__('segment_not_found')
        self.segment_id = segment_id


class ExportError(DomainError):
    pass


class ExportTriggerError(ExportError):
    def __init__(self, reason: str | None = None) -> None:
        super().__init__('export_trigger_error')
        self.reason = reason


class CoreUnavailableError(DomainError):
    def __init__(self) -> None:
        super().__init__('core_unavailable')


class ForbiddenBackofficeActionError(DomainError):
    def __init__(self) -> None:
        super().__init__('forbidden_backoffice_action')

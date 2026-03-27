class CoreApiError(Exception):
    pass


class CoreApiNetworkError(CoreApiError):
    pass


class CoreApiHttpError(CoreApiError):
    def __init__(self, status_code: int, detail: str | None = None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP error {status_code}: {detail or 'Unknown error'}")


class CoreApiNotFoundError(CoreApiHttpError):
    def __init__(self, detail: str | None = None):
        super().__init__(404, detail or "Not Found")


class CoreApiUnauthorizedError(CoreApiHttpError):
    def __init__(self, status_code: int, detail: str | None = None):
        super().__init__(status_code, detail or "Unauthorized or Forbidden")


class CoreApiDataError(CoreApiError):
    pass

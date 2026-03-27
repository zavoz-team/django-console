from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Pagination:
    limit: int
    offset: int = 0

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError('limit_invalid')
        if self.offset < 0:
            raise ValueError('offset_invalid')


@dataclass(frozen=True, slots=True, kw_only=True)
class TextQuery:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError('text_query_empty')

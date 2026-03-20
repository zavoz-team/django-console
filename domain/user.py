from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    id: str
    email: str
    name: str

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class CookieSetDTO:
    name: str
    value: str

    max_age: int | None
    path: str
    domain: str | None

    secure: bool
    httponly: bool
    samesite: Literal["Strict", "Lax", "None"]


@dataclass(frozen=True, slots=True)
class CookieDeleteDTO:
    name: str

    path: str
    domain: str | None

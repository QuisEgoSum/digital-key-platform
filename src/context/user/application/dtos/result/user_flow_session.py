from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T", bound=object)


@dataclass(frozen=True)
class UserFlowSessionCreateResult[T]:
    session_key: str
    storage: T

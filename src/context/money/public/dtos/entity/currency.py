from dataclasses import dataclass

from context.money.public.enums.currency import CurrencyCode, CurrencyKind


@dataclass()
class CurrencyDTO:
    code: CurrencyCode
    kind: CurrencyKind
    precision: int
    name: str

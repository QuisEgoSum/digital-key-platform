from enum import StrEnum


class CurrencyCode(StrEnum):
    USD = "USD"
    EUR = "EUR"
    BTC = "BTC"
    ETH = "ETH"


class CurrencyKind(StrEnum):
    FIAT = "fiat"
    CRYPTO = "crypto"

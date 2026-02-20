from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from context.wallet.public.enums.wallet import (
    OperationSource,
    OperationType,
    OwnerType,
    WalletRole,
)


@dataclass(frozen=True)
class EntryPostDTO:
    owner_id: int
    owner_type: OwnerType
    wallet_role: WalletRole
    amount: Decimal


@dataclass(frozen=True)
class OperationPostDTO:
    type: OperationType
    idempotency_key: str
    source_type: OperationSource
    source_id: UUID
    currency: str
    entries: list[EntryPostDTO]

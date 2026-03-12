from enum import StrEnum


class OwnerType(StrEnum):
    """Account Holder type."""

    USER = "user"
    SYSTEM = "system"


class WalletRole(StrEnum):
    """The role of the account for the holder."""

    USER_AVAILABLE = "user_available"
    USER_HOLD = "user_hold"
    # Internal operations, platform revenue (bue, refund order, etc).
    SYSTEM_REVENUE = "system_revenue"
    # External operations, payment provider payments.
    SYSTEM_EXTERNAL = "system_external"


class OperationType(StrEnum):
    """Type of account operation."""

    # Credits user's available balance for a confirmed deposit (incoming funds).
    # Source is a deposit/payment event.
    DEPOSIT = "deposit"
    # Charges the user for a purchase: debits user's available wallet
    # and credits platform revenue.
    PURCHASE = "purchase"
    # Reserves funds: moves amount from available to hold wallet
    # (funds remain in-system but become unavailable).
    HOLD = "hold"
    # Releases reserved funds: moves amount from hold back to available wallet.
    RELEASE = "release"
    # Executes a withdrawal: moves funds out of the hold wallet to an
    # external/system account after provider confirmation.
    WITHDRAWAL_EXECUTE = "withdrawal_execute"
    # Manual correction entry used by admins to fix incidents;
    # should be rare and accompanied by audit metadata.
    MANUAL_ADJUST = "manual_adjust"


class OperationSource(StrEnum):
    """Source of account operation."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    ORDER = "order"
    MANUAL = "manual"


class EntryDirection(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"

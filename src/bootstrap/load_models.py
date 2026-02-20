async def load_models() -> None:
    """
    Load sqlalchemy models for migrations.
    """

    import context.catalog.infra.models
    import context.money.infra.models
    import context.sale.infra.models
    import context.user.infra.models
    import context.wallet.infra.models  # noqa: F401
    import infra.audit.models  # noqa: F401

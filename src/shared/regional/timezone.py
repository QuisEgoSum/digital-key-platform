def resolve_timezone(
    explicit_timezone: str | None,
    default_timezone: str,
) -> str:
    return explicit_timezone if explicit_timezone else default_timezone

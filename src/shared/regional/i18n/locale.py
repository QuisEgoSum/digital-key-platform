import re

from collections.abc import Container, Sequence

_LOCALE_RE = re.compile(r"^[A-Za-z]{2,3}(?:[-_][A-Za-z]{2})?$")


def normalize_locale(locale: str) -> str:
    """Normalize locale to a simple BCP 47-like form.

    Examples:
        ru -> ru
        RU -> ru
        ru_RU -> ru-RU
        ru-ru -> ru-RU
        en_us -> en-US
    """
    value = locale.strip()
    if not value:
        raise ValueError("Locale must not be empty")

    if not _LOCALE_RE.fullmatch(value):
        raise ValueError(f"Invalid locale format: {locale!r}")

    parts = value.replace("_", "-").split("-")

    language = parts[0].lower()

    if len(parts) == 1:
        return language

    region = parts[1].upper()
    return f"{language}-{region}"


def try_resolve_supported_locale(
    locale: str | None,
    supported_locales: Container[str],
) -> str | None:
    if locale is None:
        return None

    try:
        normalized = normalize_locale(locale)
    except ValueError:
        return None

    if normalized in supported_locales:
        return normalized

    language = normalized.split("-", 1)[0]
    if language in supported_locales:
        return language

    return None


def resolve_supported_locale(
    explicit_locale: str | None,
    accept_locales: Sequence[str] | None,
    supported_locales: Container[str],
    default_locale: str,
) -> str:
    resolved = try_resolve_supported_locale(explicit_locale, supported_locales)
    if resolved is not None:
        return resolved

    if accept_locales:
        for candidate in accept_locales:
            resolved = try_resolve_supported_locale(candidate, supported_locales)
            if resolved is not None:
                return resolved

    return default_locale

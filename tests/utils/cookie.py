from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParsedSetCookie:
    name: str
    value: str | None
    is_deleted: bool


def parse_set_cookie(header: str) -> ParsedSetCookie:
    """Parse a single Set-Cookie header."""
    parts = [part.strip() for part in header.split(";")]
    if not parts or "=" not in parts[0]:
        raise ValueError(f"Invalid Set-Cookie header: {header!r}")

    name, value = parts[0].split("=", 1)

    is_deleted = False
    for attr in parts[1:]:
        attr_lower = attr.lower()
        if attr_lower == "max-age=0":
            is_deleted = True
            break
        if attr_lower.startswith("expires="):
            is_deleted = True
            break

    if value == "":
        is_deleted = True

    return ParsedSetCookie(
        name=name,
        value=None if is_deleted else value,
        is_deleted=is_deleted,
    )


def parse_set_cookie_headers_by_name(headers: list[str]) -> dict[str, ParsedSetCookie]:
    """Parse multiple Set-Cookie headers and index them by cookie name."""
    result: dict[str, ParsedSetCookie] = {}
    for header in headers:
        cookie = parse_set_cookie(header)
        result[cookie.name] = cookie
    return result

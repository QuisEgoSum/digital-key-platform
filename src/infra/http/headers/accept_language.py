from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AcceptLanguageItem:
    locale: str
    q: float


def parse_accept_language(value: str | None) -> list[str]:
    """Parse Accept-Language and return locales ordered by priority.

    Example:
        "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        -> ["ru-RU", "ru", "en-US", "en"]
    """
    if not value:
        return []

    items: list[AcceptLanguageItem] = []

    for raw_item in value.split(","):
        item = raw_item.strip()
        if not item:
            continue

        parts = [part.strip() for part in item.split(";")]
        locale = parts[0]

        if not locale or locale == "*":
            continue

        q = 1.0

        for part in parts[1:]:
            if not part.startswith("q="):
                continue

            try:
                q = float(part[2:])
            except ValueError:
                q = 0.0

        items.append(AcceptLanguageItem(locale=locale, q=q))

    items.sort(key=lambda v: v.q, reverse=True)
    return [v.locale for v in items if v.q > 0]

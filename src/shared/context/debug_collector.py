from contextvars import ContextVar

_debug_artifacts: ContextVar[dict[str, str]] = ContextVar("debug_artifacts")


def add_debug_artifact(name: str, value: str) -> None:
    try:
        current = _debug_artifacts.get()
    except LookupError:
        current = {}
        _debug_artifacts.set(current)

    current[name] = value


def get_debug_artifacts() -> dict[str, str]:
    try:
        return _debug_artifacts.get()
    except LookupError:
        return {}


def clear_debug_artifacts() -> None:
    _debug_artifacts.set({})

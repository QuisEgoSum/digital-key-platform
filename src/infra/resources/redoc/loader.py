from pathlib import Path

from config import config

_RAW_HTML: str | None = None


def _load() -> str:
    path = Path(config.root_dir) / "resources" / "redoc.html"
    return path.read_text(encoding="utf-8")


def get_redoc_html(docs_path: str) -> str:
    global _RAW_HTML
    if _RAW_HTML is None:
        _RAW_HTML = _load()
    return _RAW_HTML.replace("{DOC_PATH}", docs_path)

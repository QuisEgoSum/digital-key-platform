import logging
import sys

from typing import TYPE_CHECKING

import structlog

from structlog.stdlib import ProcessorFormatter

from config.models.components.logger import LoggerConfig
from infra.logging import structlog_processors
from shared.serialization.json import soft_json_dumps

if TYPE_CHECKING:
    from structlog.typing import Processor


def setup_logging(cfg: LoggerConfig) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(cfg.level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = ProcessorFormatter(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog_processors.add_label,
            ProcessorFormatter.remove_processors_meta,
            structlog.processors.EventRenamer("message"),
            structlog.stdlib.add_log_level,
            structlog_processors.uppercase_level,
            structlog.processors.format_exc_info,
            structlog_processors.add_process_name,
            structlog_processors.add_trace_ids,
            structlog_processors.gather_payload,
            structlog_processors.reorder_fields,
            _renderer(cfg),
        ],
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(cfg.level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root.addHandler(handler)


def _renderer(cfg: LoggerConfig) -> "Processor":
    if cfg.format == "plain":
        return structlog.dev.ConsoleRenderer()
    return structlog.processors.JSONRenderer(serializer=soft_json_dumps)

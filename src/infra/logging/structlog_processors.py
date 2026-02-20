from collections.abc import Mapping, MutableMapping
from logging import LogRecord
from multiprocessing.process import current_process
from typing import Any

from shared.utils.tracing import get_traces


def add_label(
    logger: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> Mapping[str, Any]:
    record = event_dict.get("_record")
    if isinstance(record, LogRecord):
        event_dict["label"] = record.name
    elif logger is not None:
        event_dict["label"] = logger.name
    return event_dict


def uppercase_level(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> Mapping[str, Any]:
    level = event_dict.get("level")
    if isinstance(level, str):
        event_dict["level"] = level.upper()
    return event_dict


def add_process_name(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> Mapping[str, Any]:
    event_dict["pname"] = current_process().name
    event_dict["pid"] = current_process().pid
    return event_dict


def add_trace_ids(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> Mapping[str, Any]:
    trace_id, span_id = get_traces()
    if trace_id:
        event_dict["trace_id"] = trace_id
        event_dict["span_id"] = span_id
    return event_dict


def gather_payload(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> Mapping[str, Any]:
    reserved_keys = {
        "message",
        "timestamp",
        "level",
        "trace_id",
        "span_id",
        "label",
        "pname",
        "pid",
        "exception",
    }
    payload = {k: v for k, v in event_dict.items() if k not in reserved_keys}
    if payload:
        event_dict["payload"] = payload
        for key in payload:
            if key == "payload":
                continue
            event_dict.pop(key)
    return event_dict


def reorder_fields(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    ordered_keys = [
        "level",
        "message",
        "timestamp",
        "trace_id",
        "span_id",
        "label",
        "pname",
        "pid",
        "payload",
        "exception",
    ]
    ordered_event_dict = {k: event_dict[k] for k in ordered_keys if k in event_dict}
    for key in event_dict:
        if key not in ordered_keys:
            ordered_event_dict[key] = event_dict[key]
    return ordered_event_dict

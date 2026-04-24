import json
import logging
from collections import defaultdict
from threading import Lock
from uuid import uuid4

from core.models import RunStatus, TraceEvent, TraceEventType


class TraceRecorder:
    def __init__(self, log_level: str = "INFO") -> None:
        logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
        self._events: dict[str, list[TraceEvent]] = defaultdict(list)
        self._lock = Lock()

    def new_trace_id(self) -> str:
        return f"tr-{uuid4().hex}"

    def emit(
        self,
        *,
        trace_id: str,
        run_id: str,
        event: TraceEventType,
        status: RunStatus | None = None,
        data: dict | None = None,
    ) -> TraceEvent:
        event_record = TraceEvent(
            trace_id=trace_id,
            run_id=run_id,
            event=event,
            status=status,
            data=data or {},
        )
        with self._lock:
            self._events[trace_id].append(event_record)
        logging.info("trace_event=%s", json.dumps(event_record.model_dump(), default=str))
        return event_record

    def get_events(self, trace_id: str) -> list[TraceEvent]:
        with self._lock:
            return list(self._events.get(trace_id, []))

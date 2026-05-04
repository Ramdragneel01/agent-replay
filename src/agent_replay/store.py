"""Thread-safe in-memory run/event store."""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from .models import EventCreateRequest, RunDetail, RunEvent, RunSummary, utc_now_iso


@dataclass
class RunRecord:
    id: str
    created_at: str
    metadata: dict[str, Any]
    events: list[RunEvent] = field(default_factory=list)


class InMemoryRunStore:
    def __init__(self, max_events_per_run: int = 5000) -> None:
        self._lock = threading.Lock()
        self._runs: dict[str, RunRecord] = {}
        self._max_events = max_events_per_run

    def create_run(self, metadata: dict[str, Any]) -> RunSummary:
        with self._lock:
            run_id = uuid.uuid4().hex
            record = RunRecord(id=run_id, created_at=utc_now_iso(), metadata=dict(metadata))
            self._runs[run_id] = record
        return RunSummary(id=record.id, created_at=record.created_at, event_count=0, metadata=record.metadata)

    def list_runs(self) -> list[RunSummary]:
        with self._lock:
            runs = list(self._runs.values())
        runs.sort(key=lambda r: r.created_at, reverse=True)
        return [
            RunSummary(id=r.id, created_at=r.created_at, event_count=len(r.events), metadata=r.metadata)
            for r in runs
        ]

    def get_run(self, run_id: str) -> RunDetail:
        with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise KeyError(f"run not found: {run_id}")
            events = list(record.events)
        return RunDetail(
            id=record.id,
            created_at=record.created_at,
            event_count=len(events),
            metadata=record.metadata,
            events=events,
        )

    def append_event(self, run_id: str, payload: EventCreateRequest) -> RunEvent:
        with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise KeyError(f"run not found: {run_id}")

            if len(record.events) >= self._max_events:
                raise ValueError("max events exceeded for run")

            used_steps = {event.step for event in record.events}
            if payload.step is None:
                step = 0 if not record.events else max(used_steps) + 1
            else:
                step = payload.step
                if step in used_steps:
                    raise ValueError(f"event step {step} already exists")

            event = RunEvent(
                step=step,
                action=payload.action,
                input=payload.input,
                output=payload.output,
                state_patch=payload.state_patch,
                ts=utc_now_iso(),
            )
            record.events.append(event)
            record.events.sort(key=lambda e: e.step)

        return event

    def list_events(self, run_id: str) -> list[RunEvent]:
        return self.get_run(run_id).events

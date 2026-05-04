"""Pydantic schemas for run/event/replay contracts."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class RunCreateRequest(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventCreateRequest(BaseModel):
    step: int | None = Field(default=None, ge=0)
    action: str = Field(min_length=1, max_length=200)
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    state_patch: dict[str, Any] = Field(default_factory=dict)


class ReplayRequest(BaseModel):
    from_step: int | None = Field(default=None, ge=0)
    to_step: int | None = Field(default=None, ge=0)
    direction: Literal["forward", "reverse"] = "forward"


class RunEvent(BaseModel):
    step: int
    action: str
    input: dict[str, Any]
    output: dict[str, Any]
    state_patch: dict[str, Any]
    ts: str


class ReplayFrame(BaseModel):
    step: int
    action: str
    state: dict[str, Any]
    ts: str


class ReplayResponse(BaseModel):
    run_id: str
    direction: Literal["forward", "reverse"]
    frames: list[ReplayFrame]


class RunSummary(BaseModel):
    id: str
    created_at: str
    event_count: int
    metadata: dict[str, Any]


class RunDetail(RunSummary):
    events: list[RunEvent]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

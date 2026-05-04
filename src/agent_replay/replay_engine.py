"""Replay primitives for forward/reverse timeline traversal."""
from __future__ import annotations

from copy import deepcopy

from .models import ReplayFrame, RunEvent


def _deep_merge(base: dict, patch: dict) -> dict:
    out = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out


def build_timeline(events: list[RunEvent]) -> list[ReplayFrame]:
    state: dict = {}
    timeline: list[ReplayFrame] = []

    for event in sorted(events, key=lambda e: e.step):
        if event.state_patch:
            state = _deep_merge(state, event.state_patch)
        if event.output:
            state = _deep_merge(state, {"last_output": event.output})

        timeline.append(
            ReplayFrame(
                step=event.step,
                action=event.action,
                state=deepcopy(state),
                ts=event.ts,
            )
        )

    return timeline


def slice_timeline(
    timeline: list[ReplayFrame],
    from_step: int | None,
    to_step: int | None,
    direction: str,
) -> list[ReplayFrame]:
    if not timeline:
        return []

    lo = timeline[0].step if from_step is None else from_step
    hi = timeline[-1].step if to_step is None else to_step

    clipped = [frame for frame in timeline if lo <= frame.step <= hi]
    if direction == "reverse":
        clipped.reverse()
    return clipped

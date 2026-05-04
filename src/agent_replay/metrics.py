"""Prometheus counters for agent replay service."""
from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

REQUESTS = Counter("agent_replay_requests_total", "Total API requests", ["endpoint", "result"])
RUNS = Counter("agent_replay_runs_total", "Runs created", ["action"])
EVENTS = Counter("agent_replay_events_total", "Events appended", ["result"])


def mark_request(endpoint: str, result: str = "ok") -> None:
    REQUESTS.labels(endpoint=endpoint, result=result).inc()


def mark_run_created() -> None:
    RUNS.labels(action="create").inc()


def mark_event_created(result: str = "ok") -> None:
    EVENTS.labels(result=result).inc()


def export_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST

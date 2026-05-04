"""FastAPI app for agent run recording and timeline replay."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .metrics import export_metrics, mark_event_created, mark_request, mark_run_created
from .models import EventCreateRequest, ReplayRequest, ReplayResponse, RunDetail, RunSummary
from .replay_engine import build_timeline, slice_timeline
from .store import InMemoryRunStore


def create_app(settings: Settings | None = None, store: InMemoryRunStore | None = None) -> FastAPI:
    settings = settings or Settings()
    store = store or InMemoryRunStore(max_events_per_run=settings.max_events_per_run)

    app = FastAPI(title="agent-replay", version="0.1.0")

    @app.get("/")
    def root() -> dict:
        mark_request("root")
        return {"service": settings.service_name, "docs": "/docs", "ui": "/ui"}

    @app.get("/health")
    def health() -> dict:
        mark_request("health")
        return {"status": "ok", "service": settings.service_name}

    @app.get("/ready")
    def ready() -> dict:
        mark_request("ready")
        return {"status": "ready"}

    @app.get("/metrics")
    def metrics() -> Response:
        payload, content_type = export_metrics()
        return Response(content=payload, media_type=content_type)

    @app.post("/v1/runs", response_model=RunSummary)
    def create_run(payload: dict | None = None) -> RunSummary:
        mark_request("create_run")
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        summary = store.create_run(metadata=metadata)
        mark_run_created()
        return summary

    @app.get("/v1/runs", response_model=list[RunSummary])
    def list_runs() -> list[RunSummary]:
        mark_request("list_runs")
        return store.list_runs()

    @app.get("/v1/runs/{run_id}", response_model=RunDetail)
    def get_run(run_id: str) -> RunDetail:
        mark_request("get_run")
        try:
            return store.get_run(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from None

    @app.post("/v1/runs/{run_id}/events")
    def append_event(run_id: str, payload: EventCreateRequest) -> dict:
        mark_request("append_event")
        try:
            event = store.append_event(run_id, payload)
            mark_event_created("ok")
            return {"run_id": run_id, "event": event}
        except KeyError as exc:
            mark_event_created("missing_run")
            raise HTTPException(status_code=404, detail=str(exc)) from None
        except ValueError as exc:
            mark_event_created("rejected")
            raise HTTPException(status_code=400, detail=str(exc)) from None

    @app.get("/v1/runs/{run_id}/events")
    def list_events(run_id: str) -> dict:
        mark_request("list_events")
        try:
            return {"run_id": run_id, "events": store.list_events(run_id)}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from None

    @app.post("/v1/runs/{run_id}/replay", response_model=ReplayResponse)
    def replay(run_id: str, payload: ReplayRequest) -> ReplayResponse:
        mark_request("replay")
        try:
            detail = store.get_run(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from None

        timeline = build_timeline(detail.events)
        frames = slice_timeline(timeline, payload.from_step, payload.to_step, payload.direction)
        return ReplayResponse(run_id=run_id, direction=payload.direction, frames=frames)

    @app.get("/v1/runs/{run_id}/timeline", response_model=ReplayResponse)
    def timeline(run_id: str) -> ReplayResponse:
        mark_request("timeline")
        try:
            detail = store.get_run(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from None

        frames = build_timeline(detail.events)
        return ReplayResponse(run_id=run_id, direction="forward", frames=frames)

    frontend_candidates = [
        Path(settings.frontend_dir),
        Path(__file__).resolve().parents[2] / settings.frontend_dir,
    ]
    frontend = next((path for path in frontend_candidates if path.exists()), None)
    if frontend is not None:
        app.mount("/ui", StaticFiles(directory=str(frontend), html=True), name="ui")

    return app


app = create_app()

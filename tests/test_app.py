from fastapi.testclient import TestClient

from agent_replay.app import create_app
from agent_replay.config import Settings
from agent_replay.store import InMemoryRunStore


def _client() -> TestClient:
    app = create_app(Settings(frontend_dir="frontend", max_events_per_run=20), InMemoryRunStore(max_events_per_run=20))
    return TestClient(app)


def _new_run(client: TestClient) -> str:
    response = client.post("/v1/runs", json={"metadata": {"label": "demo"}})
    assert response.status_code == 200
    return response.json()["id"]


def test_health_ready_root():
    c = _client()
    assert c.get("/").status_code == 200
    assert c.get("/health").json()["status"] == "ok"
    assert c.get("/ready").json()["status"] == "ready"


def test_create_get_list_run():
    c = _client()
    run_id = _new_run(c)
    detail = c.get(f"/v1/runs/{run_id}")
    listing = c.get("/v1/runs")
    assert detail.status_code == 200
    assert listing.status_code == 200
    assert any(item["id"] == run_id for item in listing.json())


def test_append_and_list_events():
    c = _client()
    run_id = _new_run(c)
    payload = {
        "action": "planner",
        "input": {"query": "hello"},
        "output": {"plan": "ok"},
        "state_patch": {"phase": "planning"},
    }
    append = c.post(f"/v1/runs/{run_id}/events", json=payload)
    events = c.get(f"/v1/runs/{run_id}/events")
    assert append.status_code == 200
    assert events.status_code == 200
    assert len(events.json()["events"]) == 1


def test_duplicate_event_step_returns_400():
    c = _client()
    run_id = _new_run(c)
    p1 = {"step": 5, "action": "a", "input": {}, "output": {}, "state_patch": {}}
    p2 = {"step": 5, "action": "b", "input": {}, "output": {}, "state_patch": {}}
    assert c.post(f"/v1/runs/{run_id}/events", json=p1).status_code == 200
    assert c.post(f"/v1/runs/{run_id}/events", json=p2).status_code == 400


def test_replay_forward_and_reverse():
    c = _client()
    run_id = _new_run(c)

    for idx, action in enumerate(["plan", "retrieve", "answer"]):
        c.post(
            f"/v1/runs/{run_id}/events",
            json={
                "step": idx,
                "action": action,
                "input": {},
                "output": {"step": action},
                "state_patch": {"phase": action},
            },
        )

    forward = c.post(f"/v1/runs/{run_id}/replay", json={"direction": "forward"})
    reverse = c.post(f"/v1/runs/{run_id}/replay", json={"direction": "reverse"})

    assert [f["step"] for f in forward.json()["frames"]] == [0, 1, 2]
    assert [f["step"] for f in reverse.json()["frames"]] == [2, 1, 0]


def test_timeline_endpoint():
    c = _client()
    run_id = _new_run(c)
    c.post(
        f"/v1/runs/{run_id}/events",
        json={"action": "plan", "input": {}, "output": {}, "state_patch": {"phase": "plan"}},
    )
    timeline = c.get(f"/v1/runs/{run_id}/timeline")
    assert timeline.status_code == 200
    assert timeline.json()["direction"] == "forward"


def test_missing_run_404():
    c = _client()
    response = c.get("/v1/runs/missing")
    assert response.status_code == 404


def test_metrics_endpoint_contains_counter_name():
    c = _client()
    text = c.get("/metrics").text
    assert "agent_replay_requests_total" in text

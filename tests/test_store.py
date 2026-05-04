import pytest

from agent_replay.models import EventCreateRequest
from agent_replay.store import InMemoryRunStore


def _event(action: str, step=None):
    return EventCreateRequest(
        step=step,
        action=action,
        input={"x": action},
        output={"y": action},
        state_patch={"phase": action},
    )


def test_create_and_list_run():
    store = InMemoryRunStore()
    run = store.create_run({"label": "demo"})
    runs = store.list_runs()
    assert len(runs) == 1
    assert runs[0].id == run.id
    assert runs[0].metadata["label"] == "demo"


def test_append_auto_step_increment():
    store = InMemoryRunStore()
    run = store.create_run({})
    e1 = store.append_event(run.id, _event("a"))
    e2 = store.append_event(run.id, _event("b"))
    assert e1.step == 0
    assert e2.step == 1


def test_append_with_explicit_step():
    store = InMemoryRunStore()
    run = store.create_run({})
    event = store.append_event(run.id, _event("x", step=7))
    assert event.step == 7


def test_duplicate_step_rejected():
    store = InMemoryRunStore()
    run = store.create_run({})
    store.append_event(run.id, _event("x", step=3))
    with pytest.raises(ValueError):
        store.append_event(run.id, _event("y", step=3))


def test_unknown_run_raises():
    store = InMemoryRunStore()
    with pytest.raises(KeyError):
        store.get_run("missing")


def test_max_events_enforced():
    store = InMemoryRunStore(max_events_per_run=1)
    run = store.create_run({})
    store.append_event(run.id, _event("x"))
    with pytest.raises(ValueError):
        store.append_event(run.id, _event("y"))

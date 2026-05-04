from agent_replay.models import RunEvent
from agent_replay.replay_engine import build_timeline, slice_timeline


def _events():
    return [
        RunEvent(step=0, action="plan", input={}, output={"plan": "ok"}, state_patch={"phase": "plan"}, ts="t0"),
        RunEvent(step=1, action="retrieve", input={}, output={"docs": 3}, state_patch={"docs": 3}, ts="t1"),
        RunEvent(step=2, action="answer", input={}, output={"answer": "done"}, state_patch={"phase": "answer"}, ts="t2"),
    ]


def test_build_timeline_merges_state_and_output():
    timeline = build_timeline(_events())
    assert len(timeline) == 3
    assert timeline[0].state["phase"] == "plan"
    assert timeline[1].state["docs"] == 3
    assert "last_output" in timeline[2].state


def test_slice_timeline_forward_range():
    timeline = build_timeline(_events())
    frames = slice_timeline(timeline, from_step=1, to_step=2, direction="forward")
    assert [f.step for f in frames] == [1, 2]


def test_slice_timeline_reverse_range():
    timeline = build_timeline(_events())
    frames = slice_timeline(timeline, from_step=0, to_step=2, direction="reverse")
    assert [f.step for f in frames] == [2, 1, 0]


def test_slice_empty_timeline():
    assert slice_timeline([], None, None, "forward") == []

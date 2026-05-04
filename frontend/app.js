const runIdInput = document.getElementById("run-id");
const loadBtn = document.getElementById("load");
const seedBtn = document.getElementById("seed");
const slider = document.getElementById("step-slider");
const stepLabel = document.getElementById("step-label");
const frameEl = document.getElementById("frame");
const metaEl = document.getElementById("meta");
const forwardBtn = document.getElementById("play-forward");
const reverseBtn = document.getElementById("play-reverse");

let frames = [];
let runId = "";
let timer = null;

function renderFrame(index) {
  if (!frames.length) {
    frameEl.textContent = "{}";
    stepLabel.textContent = "step: 0";
    return;
  }
  const clamped = Math.max(0, Math.min(frames.length - 1, index));
  const frame = frames[clamped];
  slider.value = String(clamped);
  stepLabel.textContent = `step: ${frame.step}`;
  frameEl.textContent = JSON.stringify(frame, null, 2);
}

function stopPlayback() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

async function loadTimeline(id) {
  const [runResp, timelineResp] = await Promise.all([
    fetch(`/v1/runs/${id}`),
    fetch(`/v1/runs/${id}/timeline`)
  ]);

  if (!runResp.ok || !timelineResp.ok) {
    throw new Error("Failed to load run/timeline");
  }

  const run = await runResp.json();
  const timeline = await timelineResp.json();

  runId = id;
  frames = timeline.frames || [];
  slider.max = String(Math.max(0, frames.length - 1));
  slider.value = "0";
  metaEl.textContent = JSON.stringify(run, null, 2);
  renderFrame(0);
}

async function createDemoRun() {
  const runRes = await fetch("/v1/runs", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ metadata: { label: "demo-run" } })
  });

  if (!runRes.ok) throw new Error("Failed to create demo run");
  const run = await runRes.json();

  const demoEvents = [
    {
      action: "planner",
      input: { query: "Summarize incident" },
      output: { plan: "collect logs" },
      state_patch: { phase: "planning", steps: 1 }
    },
    {
      action: "retriever",
      input: { source: "incident-db" },
      output: { docs: 4 },
      state_patch: { phase: "retrieval", docs: 4 }
    },
    {
      action: "responder",
      input: { style: "executive" },
      output: { answer: "incident resolved" },
      state_patch: { phase: "answering", status: "resolved" }
    }
  ];

  for (const event of demoEvents) {
    const res = await fetch(`/v1/runs/${run.id}/events`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(event)
    });
    if (!res.ok) throw new Error("Failed to append demo event");
  }

  runIdInput.value = run.id;
  await loadTimeline(run.id);
}

function playback(direction) {
  stopPlayback();
  if (!frames.length) return;

  let idx = Number(slider.value || 0);
  timer = setInterval(() => {
    idx += direction === "forward" ? 1 : -1;
    if (idx < 0 || idx >= frames.length) {
      stopPlayback();
      return;
    }
    renderFrame(idx);
  }, 450);
}

loadBtn.addEventListener("click", async () => {
  stopPlayback();
  const id = runIdInput.value.trim();
  if (!id) return;
  try {
    await loadTimeline(id);
  } catch (err) {
    alert((err && err.message) || "Unable to load run");
  }
});

seedBtn.addEventListener("click", async () => {
  stopPlayback();
  try {
    await createDemoRun();
  } catch (err) {
    alert((err && err.message) || "Unable to create demo run");
  }
});

slider.addEventListener("input", () => {
  stopPlayback();
  renderFrame(Number(slider.value));
});

forwardBtn.addEventListener("click", () => playback("forward"));
reverseBtn.addEventListener("click", () => playback("reverse"));

# agent-replay

Time-travel debugger for agent runs: record step events, replay timeline state forward/reverse, and inspect snapshots in a browser UI.

[![CI](https://github.com/Ramdragneel01/agent-replay/actions/workflows/ci.yml/badge.svg)](https://github.com/Ramdragneel01/agent-replay/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Why

Agent failures are hard to debug because logs are linear but behavior is stateful. `agent-replay` captures stepwise run events and lets you scrub state as if you had a debugger timeline.

## Capabilities

- Create runs and append structured events
- Build state snapshots from per-step patches
- Replay timeline:
  - forward
  - reverse
  - range-limited
- Browser UI for timeline scrubbing and frame inspection
- Metrics + operational endpoints

## Quick Start

```bash
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
pip install -e .
python -m agent_replay
```

API root: http://localhost:8095
UI: http://localhost:8095/ui

## API Endpoints

- GET `/health`
- GET `/ready`
- GET `/metrics`
- POST `/v1/runs`
- GET `/v1/runs`
- GET `/v1/runs/{run_id}`
- POST `/v1/runs/{run_id}/events`
- GET `/v1/runs/{run_id}/events`
- POST `/v1/runs/{run_id}/replay`
- GET `/v1/runs/{run_id}/timeline`

## Example

Create run:

```bash
curl -X POST http://localhost:8095/v1/runs -H "content-type: application/json" -d "{\"metadata\":{\"agent\":\"support-bot\"}}"
```

Append event:

```bash
curl -X POST http://localhost:8095/v1/runs/<run_id>/events \
  -H "content-type: application/json" \
  -d "{\"action\":\"planner\",\"state_patch\":{\"phase\":\"planning\"},\"output\":{\"plan\":\"collect docs\"}}"
```

Replay reverse:

```bash
curl -X POST http://localhost:8095/v1/runs/<run_id>/replay \
  -H "content-type: application/json" \
  -d "{\"direction\":\"reverse\"}"
```

## Docker

```bash
docker compose up --build
```

## Testing

```bash
ruff check src tests
pytest
```

Current baseline: 18 passing tests.

## Architecture and Ops

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Security: [SECURITY.md](SECURITY.md)
- Runbook: [docs/RUNBOOK.md](docs/RUNBOOK.md)

## Roadmap

- Diff view between selected timeline frames
- OpenTelemetry span import/export
- Persistent run store (SQLite/Postgres)
- Agent protocol adapters (LangGraph, CrewAI, custom)

## License

MIT

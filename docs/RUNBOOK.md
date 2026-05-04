# Runbook

## Service

- default port: 8095
- health: `GET /health`
- readiness: `GET /ready`
- ui: `GET /ui`

## Startup

```bash
pip install -r requirements-dev.txt
pip install -e .
python -m agent_replay
```

## Smoke Checks

```bash
curl http://localhost:8095/health
curl http://localhost:8095/ready
curl http://localhost:8095/v1/runs
```

## Incident Playbooks

### Replay returns empty frames unexpectedly

1. Verify events exist: `GET /v1/runs/{id}/events`
2. Check requested `from_step`/`to_step` range
3. Confirm event steps are not duplicated/rejected

### Run creation works but event append fails

1. Validate run id is correct
2. Check max-events-per-run setting
3. Inspect duplicate step collisions

### UI timeline not updating

1. Verify API and UI served from same process
2. Check browser devtools network for `/v1/runs/*`
3. Ensure run id exists and timeline has frames

# Architecture

## Objective

Provide a deterministic replay engine that reconstructs agent state across event steps and supports time-travel inspection in both API and UI workflows.

## Components

- API (`src/agent_replay/app.py`)
  - run/event CRUD-like endpoints
  - replay/timeline endpoints
  - health, ready, metrics
- Store (`src/agent_replay/store.py`)
  - thread-safe in-memory run/event persistence
- Replay Engine (`src/agent_replay/replay_engine.py`)
  - state patch application
  - timeline frame generation
  - directional/range slicing
- UI (`frontend/*`)
  - load run
  - scrub timeline slider
  - play forward/reverse

## Replay Semantics

- Events are sorted by step.
- Each event can carry `state_patch` and `output`.
- `state_patch` is deep-merged into aggregate state.
- Latest event output is materialized under `state.last_output`.

This guarantees reproducible frame reconstruction for a given event stream.

## Deployment Topology

- Single FastAPI process with mounted static UI.
- Stateless app process, in-memory run store (v0.1).

Mermaid source: `docs/assets/architecture.mmd`

## Future Evolution

- External store for multi-instance durability
- Snapshot compaction for long runs
- Authn/authz middleware for multi-tenant use

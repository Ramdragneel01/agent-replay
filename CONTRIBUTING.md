# Contributing

## Setup

```bash
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
pip install -e .
pytest
```

## Expectations

- Keep replay semantics deterministic.
- Add tests for any API contract or state merge behavior change.
- Avoid introducing hidden side effects in replay engine.

## Pull Requests

- one focused change per PR
- include test evidence
- keep lint/tests green

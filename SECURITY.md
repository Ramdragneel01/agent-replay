# Security Policy

## Reporting

Please report vulnerabilities privately:

- ramprakashdhulipudi@gmail.com

## Threat Model (v0.1)

In scope:
- malformed event payload abuse
- high-volume event flooding on a run
- accidental exposure of sensitive event data in logs

Out of scope:
- multi-tenant auth and role controls
- encrypted persistence at rest (in-memory only v0.1)

## Baseline Controls

- schema validation on all event/replay payloads
- max-events-per-run limit guard
- explicit error handling for missing runs and duplicate steps
- no shell execution or arbitrary code eval paths

## Hardening Recommendations

- add API authentication for non-local deployments
- move to encrypted persistent store with tenant partitioning
- add payload size limits and rate limiting middleware
- integrate audit log redaction for sensitive keys

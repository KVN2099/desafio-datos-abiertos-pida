## Cursor Agent Instructions: Vibe Coding a Databricks App

These instructions set strong defaults so you can move fast while keeping code production‑ready. Follow the checklists and only deviate with a clear reason.

### Objectives
- Ship small, vertical slices end‑to‑end.
- Prefer reproducibility over manual steps; everything should be runnable from the CLI.
- Default to safety: no destructive ops without guards, no secrets in code, no ad‑hoc state.
- Leave observability breadcrumbs: structured logs, metrics, and docs.

## Repository Layout
- `Databricks App/`
  - `app.py`: App entrypoint
  - `app.yml`: App manifest/config
  - `requirements.txt`: Runtime dependencies
- `Datos contraloria/`: Read‑only source CSVs
- `README.md`: Project overview
- `instructions.md`: This file

### Ground rules
- Treat `Datos contraloria/` as immutable input. Do not modify or re‑serialize these files.
- Prefer Unity Catalog objects and Delta tables for any derived data.
- Keep configs in code or environment; never in the data layer.

## Agent Playbook (Do This in Order)
1) Setup local environment
2) Lint, format, type‑check on every edit
3) Implement a thin, testable change
4) Dry‑run locally (no destructive ops)
5) Validate manifest and deploy via CLI (or import as fallback)
6) Smoke test on workspace
7) Open PR with runbook and acceptance evidence

## Quick Setup (Local)
1) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -V
```

2) Install dependencies
```bash
pip install -r "Databricks App/requirements.txt"
pip install ruff==0.6.9 black==24.10.0 mypy==1.13.0 pytest==8.3.3 structlog==24.4.0
```

3) Configure Databricks CLI (non‑interactive via env is preferred)
```bash
export DATABRICKS_HOST="https://<your-workspace-host>"
export DATABRICKS_TOKEN="<your-token>"
databricks --version
```
Optional named profile:
```bash
databricks configure --profile default
```

4) Sanity checks
```bash
databricks workspace ls /
python "Databricks App/app.py" --help || true
```

## Day‑to‑Day Workflow
- Lint and format before any commit
```bash
ruff check . && ruff format .
black .
```
- Type check fast paths
```bash
mypy "Databricks App" --install-types --non-interactive
```
- Run tests (if present)
```bash
pytest -q
```
- Keep commits focused. One feature/fix per PR. Include a short runbook in the PR description with: inputs, command to run, expected artifacts.

## App Development Guidelines
- Keep `app.py` as a thin orchestrator. Push business logic into small, testable modules.
- Use explicit configurations. Example environment variables:
  - `APP_CATALOG`, `APP_SCHEMA` for Unity Catalog targets
  - `APP_ENV` for environment switching (dev/stg/prd)
- Never hardcode workspace paths; parameterize with env/config.
- Use structured logging (e.g., structlog) and log key parameters and output locations.

### Data and Tables
- Use Delta Lake for all derived datasets. Prefer idempotent `merge` over overwrite.
- Partition only when it materially helps reads/writes. Don’t over‑partition small tables.
- If streaming is introduced, persist checkpoints in a per‑env location with retention.

### Secrets and Credentials
- Never commit secrets. For Databricks runtime usage, prefer Secret Scopes or UC secrets.
- In local mode, read from environment variables and fail fast if missing.

### Observability
- Log: operation name, input sizes/row counts, output paths, table names, duration.
- If MLflow is introduced, always set experiment and log params/metrics/artifacts.

## App Manifest (`app.yml`)
- Keep the manifest minimal and explicit. Typical fields:
  - name, description
  - runtime/version or policy reference
  - entrypoint (e.g., `app.py` with args)
  - permissions (principals, least‑privilege)
  - environment variables and secrets references
- Validate changes by rendering and diffing before deploy.

## Deployment Patterns
- Prefer automated deploys via CLI. Two safe options depending on feature availability:

Option A: Lakehouse Apps (if `databricks apps` is available in your workspace)
```bash
# Example sketch; adapt to your manifest
databricks apps validate --manifest "Databricks App/app.yml"
databricks apps deploy --manifest "Databricks App/app.yml" --force
```

Option B: Workspace import of app files (fallback)
```bash
TARGET_PATH="/Apps/desafio-datos-abiertos-pida"
databricks workspace import-dir -o "Databricks App" "$TARGET_PATH"
```

Post‑deploy smoke test
- Confirm the app starts and reads source CSVs without mutation.
- Verify logs and any derived Delta outputs (if created) exist and are readable.

## Safety Checklist (run before merging)
- No secrets or tokens in code, logs, or `app.yml`.
- All paths parameterized; no user‑specific local paths.
- Lint, format, type checks clean.
- Clear, deterministic entrypoint with example command in PR.
- No destructive operations (drop/overwrite) without `--confirm` or equivalent guard.

## Common Commands You Can Run
```bash
# Activate env
source .venv/bin/activate

# Lint/format
ruff check . && ruff format . && black .

# Type check
mypy "Databricks App" --install-types --non-interactive

# Tests
pytest -q

# Local dry run (adapt flags if app supports CLI args)
python "Databricks App/app.py" --env dev --dry-run

# Validate and deploy (Apps API available)
databricks apps validate --manifest "Databricks App/app.yml"
databricks apps deploy --manifest "Databricks App/app.yml" --force

# Fallback: import to workspace
TARGET_PATH="/Apps/desafio-datos-abiertos-pida"
databricks workspace import-dir -o "Databricks App" "$TARGET_PATH"
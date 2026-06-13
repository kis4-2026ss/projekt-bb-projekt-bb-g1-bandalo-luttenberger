# GuardRail — Claude Code Instructions

## What this project is

GuardRail is a Python tool that hooks into Claude Code's `PreToolUse` event to intercept and block access to forbidden file paths. It runs on a Raspberry Pi as a controlled experiment environment.

The research question: does explicitly naming forbidden paths in a prompt change how often Claude Code tries to access them?

## Project layout

```
PLAN.md                      ← full implementation plan
PROPOSAL.md                  ← project proposal
.github/workflows/ci.yml     ← GitHub Actions (ruff + pytest on every push)

guardrail/                   ← Python project root (pyproject.toml, uv.lock here)
  guardrail/                 ← Python package
    policy.py                ← loads + validates guardrail.yaml
    matcher.py               ← path resolution + glob matching
    verdict.py               ← allow / warn / block logic
    hook.py                  ← entry point called by Claude Code
    logger.py                ← writes to guardrail-audit.jsonl
    report.py                ← reads audit log, prints summary
  tests/
    test_policy.py
  scripts/
    setup_sandbox.sh         ← creates honeypot filesystem on the Pi
    run_experiment.sh        ← runs one experiment condition (A–E)
    pi_deploy.sh             ← git pull + uv sync on the Pi
  guardrail.yaml             ← policy config (forbidden paths + patterns)
  results/                   ← experiment .jsonl logs go here
```

## Dev setup

All commands must be run from inside the `guardrail/` directory:

```bash
cd guardrail
uv sync
uv run pytest
uv run ruff check
```

## Before every commit or push

Always run both checks from inside `guardrail/` and make sure they pass before committing or pushing:

```bash
cd guardrail && uv run ruff check && uv run pytest
```

If ruff fails, fix the lint errors first. If pytest fails, fix the tests first. Never push with failing checks — the CI will catch it anyway and a red action is worse than a local fix.

## Key conventions

- All paths in `guardrail/guardrail.yaml` use `~` — `policy.py` expands them to absolute paths at load time.
- The hook exits with code 1 to block a tool call, 0 to allow it.
- Experiment results go in `guardrail/results/` as `.jsonl` files, one per run.
- Scripts in `guardrail/scripts/` are meant to be run **on the Pi** via a RustDesk terminal, not on the dev machine.
- Connect to the Pi via RustDesk — not SSH.

## Work split

| Module | Owner |
|---|---|
| `policy.py` + tests | Fabian (done) |
| `matcher.py` + tests | Lukas |
| `verdict.py`, `hook.py` + tests | Lukas |
| `logger.py`, `report.py` | Fabian |
| `scripts/setup_sandbox.sh` | Fabian (done) |
| `scripts/run_experiment.sh` | Fabian |
| Analysis + presentation | Both |

# Agent Workflow Designer

Design production-grade multi-agent workflows: clear pattern choice
(sequential, parallel, hierarchical/router/orchestrator/evaluator), handoff
contracts, failure handling, and cost/context controls. Two deterministic
scripts do the mechanical work — pattern scaffolding and regression checks —
so the design effort goes into dependencies, contracts, and budgets.

## Usage

```bash
# scaffold from a pattern name
python3 scripts/workflow_scaffolder.py sequential --name content-pipeline

# scaffold from a persisted spec file and save it
python3 scripts/workflow_scaffolder.py assets/sample_spec_orchestrator.json \
    -o workflows/incident-triage.json

# regenerate-and-verify every template against expected_outputs/
python3 scripts/check_skeletons.py

# validate a spec file's shape
python3 scripts/check_skeletons.py assets/sample_spec_router.json
```

Every script documents itself: run it with `--help` for all flags.

## What you get

- `scripts/workflow_scaffolder.py` — skeleton configuration for five
  patterns, from a pattern name or a spec JSON (`{"pattern", "name"}`);
  prints to stdout, writes a file with `-o`.
- `scripts/check_skeletons.py` — template regression check (byte-exact vs
  `expected_outputs/`) and spec validation.
- `assets/` — one spec file per pattern plus a worked scenario brief.
- `references/` — pattern trade-offs, handoff contracts, failure handling,
  cost/context controls.

## Design method

1. Pick the smallest pattern that fits the dependency shape
   (`references/workflow-patterns.md`).
2. Scaffold the configuration.
3. Define a handoff contract for every edge
   (`references/handoff_contracts.md`).
4. Add retry parameters, timeouts, and validation gates
   (`references/failure_handling.md`).
5. Dry-run with small context budgets before scaling
   (`references/cost_context_controls.md`).

## Example

`python3 scripts/workflow_scaffolder.py sequential --name content-pipeline`
prints:

```json
{
  "name": "content-pipeline",
  "pattern": "sequential",
  "steps": [
    {"id": "research", "agent": "researcher", "next": "draft"},
    {"id": "draft", "agent": "writer", "next": "review"},
    {"id": "review", "agent": "reviewer", "next": null}
  ],
  "retry": {"max_attempts": 2, "backoff_seconds": 2}
}
```

Dependencies: Python standard library only. Works on Python 3.8+.

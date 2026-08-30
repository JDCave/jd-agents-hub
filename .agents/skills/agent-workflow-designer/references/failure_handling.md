# Failure Handling

How each pattern fails, and what to configure before scaling a workflow.

## Per-step policy

Every step that calls an external model or service declares:

- `retry.max_attempts` — bounded retries (2–3; external-model calls rarely
  recover beyond that)
- `retry.backoff_seconds` — delay growth between attempts
- `timeout_seconds` — wall-clock deadline, after which the attempt counts as
  failed

Sequential skeletons ship `retry` defaults; add `timeout_seconds` per step in
your configuration.

## On-fail strategies

| Strategy | Use when |
| --- | --- |
| `halt` | Downstream steps are meaningless without this output (sequential default) |
| `skip` | The branch is optional; fan-in tolerates fewer sources (mark partial) |
| `fallback` | A cheaper/generalist path can produce an acceptable answer (router default) |
| `revise_and_retry` | The failure is a quality-gate verdict, not an infrastructure error (evaluator default) |
| `degrade` | Model or budget exhausted; retry with a smaller context or cheaper model |

## Pattern-specific failure semantics

- `sequential` — a step exhausting retries halts the chain; the run reports
  the failing step id, never a partial merge.
- `parallel` — one slow branch must not stall the join:
  `timeouts.per_task_seconds` fails the branch, `fan_in_seconds` bounds the
  wait; the synthesizer receives a partial-sources list.
- `router` — unknown or low-confidence intents go to `fallback`; dropping
  unmatched work silently is forbidden.
- `orchestrator` — `completion_policy` decides whether one failed required
  task fails the run; the planner replans at most once around a failed task.
- `evaluator` — after `max_iterations`, the draft is rejected and reported;
  it is never shipped because the loop gave up.

## Validation gates

Place a schema check (required fields of the handoff contract) at every edge
before fan-in. A contract violation is a bug in the producing step: fail that
step, keep the run diagnosable, and surface the violating payload in the run
report.

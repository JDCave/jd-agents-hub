# Workflow Patterns

The five patterns `scripts/workflow_scaffolder.py` scaffolds. Snippets show the
skeleton fields; full skeletons live in `expected_outputs/` and are verified by
`scripts/check_skeletons.py`.

## Sequential

Use when each step depends on the prior step's output and the order is fixed.

- Shape: `steps[]` with explicit `next` pointers, ending in `null`.
- Failure semantics: a failed step halts the chain; `retry.max_attempts` and
  `retry.backoff_seconds` apply per step before halting.
- Watch out for: the slowest stage gates total throughput.

```json
{"pattern": "sequential", "steps": [{"id": "research", "agent": "researcher", "next": "draft"}]}
```

## Parallel

Use when subtasks are independent and a synthesis step can consume their
outputs together.

- Shape: `fan_out.tasks[]` executed by one agent role, then `fan_in` with a
  named output artifact.
- Failure semantics: `timeouts.per_task_seconds` bounds each branch;
  `timeouts.fan_in_seconds` bounds the join.
- Watch out for: fan-in blocking forever on one slow branch — always set both
  timeouts.

```json
{"pattern": "parallel", "fan_out": {"tasks": ["a", "b", "c"], "agent": "analyst"},
 "fan_in": {"agent": "synthesizer", "output": "combined_report"}}
```

## Router

Use when work must be dispatched to specialists by intent or type.

- Shape: `router.routes[]` matched by the router agent, `handlers{}` mapping
  each route to a specialist, `fallback` for unmatched intents.
- Failure semantics: unknown or low-confidence intents land on `fallback` —
  never drop silently.
- Watch out for: route sprawl; if a route needs > 3 unique steps, it is
  probably a nested sequential workflow, not a handler.

```json
{"pattern": "router", "router": {"agent": "router", "routes": ["sales", "support"]},
 "fallback": {"agent": "generalist"}}
```

## Orchestrator

Use when the plan cannot be fixed up front: steps and dependencies are decided
at run time.

- Shape: `orchestrator.planning: "dynamic"`, `specialists[]`, `execution`
  with `dependency_mode: "dag"`, `max_parallel`, `completion_policy`.
- Failure semantics: `completion_policy: "all_required"` fails the run when any
  required task fails; partial results are reported, not discarded.
- Watch out for: the planner becoming a bottleneck; bound `max_parallel` and
  replanning depth.

```json
{"pattern": "orchestrator", "orchestrator": {"agent": "orchestrator", "planning": "dynamic"},
 "execution": {"dependency_mode": "dag", "max_parallel": 3, "completion_policy": "all_required"}}
```

## Evaluator

Use when output must pass a quality gate before it is accepted.

- Shape: `generator` + `evaluator` with `criteria[]`, `loop.max_iterations`,
  `loop.pass_threshold`, `loop.on_fail`.
- Failure semantics: on gate failure the loop applies `on_fail`
  (`revise_and_retry`); after `max_iterations` the draft is rejected, not
  silently shipped.
- Watch out for: evaluators that always fail (threshold too strict) or always
  pass (criteria too vague) — calibrate on known-good and known-bad samples.

```json
{"pattern": "evaluator", "evaluator": {"agent": "evaluator", "criteria": ["accuracy", "format"]},
 "loop": {"max_iterations": 3, "pass_threshold": 0.8, "on_fail": "revise_and_retry"}}
```

## Choosing

| Dependency shape | Pattern |
|---|---|
| Fixed linear chain | `sequential` |
| Independent subtasks, one synthesis | `parallel` |
| Dispatch by intent/type | `router` |
| Dynamic plan, run-time dependencies | `orchestrator` |
| Draft must pass a quality gate | `evaluator` (wrap any of the above) |

Rules of thumb:

- Start with the smallest pattern that satisfies the requirement; grow only on
  evidence of failure, not anticipation of complexity.
- Patterns compose: a `router` handler can be a `sequential` chain; an
  `evaluator` can wrap any generator stage.
- Every edge needs a handoff contract (`handoff_contracts.md`) and every step
  needs failure and budget settings (`failure_handling.md`,
  `cost_context_controls.md`).

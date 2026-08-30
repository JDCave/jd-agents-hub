---
name: "agent-workflow-designer"
version: "1.1.0"
description: "Design production-grade multi-agent workflows with clear pattern choice (sequential, parallel, router, orchestrator, evaluator), handoff contracts, failure handling, and cost/context controls. Use when architecting a multi-step agent pipeline, choosing between single-agent vs multi-agent approaches, or refactoring an LLM workflow that suffers from context bloat or unreliable handoffs."
when_to_use: "Architecting a multi-step agent pipeline; deciding single-agent vs multi-agent; scaffolding a workflow configuration from a pattern; refactoring a workflow with context bloat or unreliable handoffs."
---

# Agent Workflow Designer

Design deterministic workflow structure before implementation: pattern choice, handoff contracts, failure handling, and cost/context controls for multi-agent systems.

## Quick Start

```bash
# scaffold from a pattern name (prints the skeleton JSON)
python3 scripts/workflow_scaffolder.py sequential --name content-pipeline
# scaffold from a spec file and save it
python3 scripts/workflow_scaffolder.py assets/sample_spec_router.json -o workflows/request-triage.json
# verify every template still matches expected_outputs/
python3 scripts/check_skeletons.py
```

A spec file is the pattern decision persisted as data:

```json
{"pattern": "router", "name": "request-triage", "notes": "dispatch by intent"}
```

## Overview

- Pattern selection for multi-step agent systems (dependency shape → pattern)
- Skeleton configuration generation for fast bootstrapping
- Handoff contracts, retry parameters, and validation gates
- Context and cost discipline across long-running flows

## When to Use

- A single prompt is insufficient for task complexity
- You want specialist agents with explicit boundaries and deterministic structure before implementation
- You need quality or safety gates on intermediate outputs
- An existing pipeline suffers context bloat or unreliable hand-offs

## Pattern Map

- `sequential`: strict step-by-step dependency chain
- `parallel`: fan-out/fan-in for independent subtasks
- `router`: dispatch by intent/type with fallback
- `orchestrator`: planner coordinates specialists with dependencies
- `evaluator`: generator + quality gate loop

Trade-offs and failure semantics per pattern: `references/workflow-patterns.md`

## Workflow

1. Select the pattern from dependency shape and risk profile.
2. Scaffold the configuration via `scripts/workflow_scaffolder.py` — pattern name or spec file.
3. Define a handoff contract for every edge (`references/handoff_contracts.md`).
4. Add retry parameters, timeouts, and output validation gates (`references/failure_handling.md`).
5. Dry-run with small context budgets before scaling (`references/cost_context_controls.md`).

## Verification

After scaffolding or editing skeletons:

```bash
python3 scripts/check_skeletons.py                 # templates vs expected_outputs/
python3 scripts/check_skeletons.py my_spec.json    # validate one spec file
```

## Common Pitfalls

- Over-orchestrating tasks solvable by one well-structured prompt
- Missing timeout/retry policies for external-model calls
- Passing full upstream context instead of targeted artifacts
- Ignoring per-step cost accumulation

## References

- `references/workflow-patterns.md` — the five patterns, selection heuristics, failure semantics
- `references/handoff_contracts.md` — required fields for every handoff edge
- `references/failure_handling.md` — retry, timeout, and degradation strategies
- `references/cost_context_controls.md` — context and cost discipline

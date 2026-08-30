# Handoff Contracts

Every edge between agents passes an explicit, bounded payload. A handoff
contract is the schema of that payload; without one, hand-offs degrade into
"forward everything", which is how context bloat and silent coupling start.

## Minimum contract (every edge)

| Field | Type | Purpose |
| --- | --- | --- |
| `workflow_id` | str | Correlate all steps of one run |
| `step_id` | str | Identity of the producing step |
| `task` | str | The instruction the consumer must act on |
| `constraints` | object | Hard limits: timeout, budget, style rules |
| `upstream_artifacts` | list | Named pointers to prior outputs (references, not transcripts) |
| `budget_tokens` | int | Context/cost budget allotted to the consumer |
| `timeout_seconds` | int | Wall-clock deadline for the consumer |

## Full contract (fan-in and evaluator edges)

Add these where multiple branches join or a gate decides acceptance:

- `source_steps[]` — which branches contributed
- `acceptance_criteria` — what the gate checks (evaluator edges)
- `rejection_policy` — `revise_and_retry` | `halt` | `degrade`
- `checksum` — integrity of the artifact payload, when reproducibility matters

## Rules

1. Artifacts, not transcripts. `upstream_artifacts` names files or records;
   it never carries a raw conversation.
2. Bounded by default. Every payload declares `budget_tokens` and
   `timeout_seconds`; a missing value is a contract bug, not a liberty.
3. Validate before fan-in. A branch whose payload fails the contract is
   failed fast (see `failure_handling.md`) rather than joined and discovered
   later.
4. Contracts are data. Keep them in the workflow configuration next to the
   step definition, so scaffolding (`workflow_scaffolder.py -o`) captures
   them.

## Example

```json
{
  "workflow_id": "content-pipeline-018f",
  "step_id": "research",
  "task": "Produce cited notes for section 2",
  "constraints": {"max_sources": 10, "style": "bullets"},
  "upstream_artifacts": [{"name": "outline", "ref": "artifacts/outline.md"}],
  "budget_tokens": 8000,
  "timeout_seconds": 180
}
```

# Cost and Context Controls

Long-running multi-agent workflows fail financially before they fail
technically: context accumulates per step, and every hand-off re-reads it.
These controls keep cost and context bounded.

## Pass artifacts, not transcripts

The single highest-leverage rule. Each hand-off payload carries named
artifacts (`upstream_artifacts`) — files or records the consumer reads on
demand — instead of the full upstream conversation. A 40k-context research
transcript becomes a 2k notes artifact.

## Budget per step

- Declare `budget_tokens` in every handoff contract; treat a missing budget
  as a configuration bug.
- Track spend per `step_id`, not just per run — per-step cost accumulation is
  invisible in run-level totals until it is 10x the estimate.
- Alert when a step exceeds 1.5x its budget; halve the budget or split the
  step.

## Context discipline

- Summarize at hand-off: the consumer gets the artifact plus a digest, not
  the source material.
- Cap `upstream_artifacts` (≤ 5 pointers per edge); more indicates the step
  is doing two steps' work.
- Prefer re-deriving cheap facts over caching them in context.

## Model and effort tiering

- Degrade per step: route mechanical steps (formatting, extraction) to
  cheaper models; reserve strong models for synthesis and gating.
- Use the `degrade` on-fail strategy when a step exhausts budget: smaller
  context, then cheaper model, then fail.

## Dry-run before scaling

Run the scaffolded workflow with small `budget_tokens` and synthetic inputs;
confirm per-step spend and payload sizes match the plan before real traffic.
`check_skeletons.py` verifies the configuration shape; a dry run verifies the
economics.

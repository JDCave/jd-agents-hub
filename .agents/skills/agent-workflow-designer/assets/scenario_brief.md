# Sample Scenario: Newsletter Digest Service

A brief of the kind this workflow design process starts from. Pattern choice
and the resulting spec file are shown below; both are working inputs for
`scripts/workflow_scaffolder.py`.

## Brief

Produce a weekly newsletter: monitor 12 sources, summarize what changed for
each, draft one digest, and gate it on factual accuracy before it is sent.
Sources are independent; the digest needs all of them; accuracy is
non-negotiable.

## Reasoning

- Monitoring 12 sources with no interdependencies → fan-out/fan-in →
  `parallel`.
- Accuracy is a hard acceptance requirement → wrap the drafting step in an
  `evaluator` loop.
- No dispatch-by-intent (not `router`), no dynamic planning (not
  `orchestrator`), and more than one stage (not plain `sequential`).

## Resulting spec

```json
{
  "pattern": "evaluator",
  "name": "newsletter-digest",
  "notes": "generator drafts the digest; evaluator gates on accuracy, format, safety"
}
```

Scaffold it (see `sample_spec_evaluator.json` for the same spec as a file):

```bash
python3 scripts/workflow_scaffolder.py evaluator --name newsletter-digest
```

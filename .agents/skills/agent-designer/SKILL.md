---
name: "agent-designer"
version: "1.1.0"
description: "Use when the user asks to design a multi-agent system, pick an orchestration pattern (supervisor/swarm/pipeline), generate provider-ready tool schemas for agents, or evaluate agent execution logs for cost, latency, and performance bottlenecks. Examples: 'design an agent architecture for research automation', 'generate Anthropic tool schemas from these tool descriptions', 'analyze these agent run logs for bottlenecks'. NOT for Claude Code workflow files (use workflow-builder) or single-agent prompt design (use agent-workflow-designer)."
when_to_use: "Designing a multi-agent system from requirements; generating Anthropic/OpenAI tool schemas from plain descriptions; evaluating agent execution logs for cost, latency, and bottlenecks."
---

# Agent Designer — Multi-Agent System Architecture

Design, schema-generate, and evaluate multi-agent systems with four deterministic scripts. The scripts are the workflow — do not freehand an architecture when the planner can score one from requirements.

## Quick Start

```bash
# 1. design an architecture from requirements
python3 scripts/agent_planner.py assets/sample_system_requirements.json -o arch
# 2. generate provider-ready tool schemas
python3 scripts/tool_schema_generator.py assets/sample_tool_descriptions.json --validate -o tools
# 3. evaluate execution logs
python3 scripts/agent_evaluator.py assets/sample_execution_logs.json --detailed -o eval
# 4. verify output shape has not drifted
python3 scripts/check_outputs.py
```

All commands run from this folder. Without `-o`, each generator prints its JSON to stdout.

## When to use

- Designing a new multi-agent system from requirements (pattern choice, roles, comms)
- Generating tool schemas (Anthropic + OpenAI formats) from plain tool descriptions
- Evaluating execution logs: success rate, latency distribution, cost, bottlenecks

**When NOT to use:** Claude Code Workflow-tool automations → `workflow-builder`; single-agent workflow scaffolds → `agent-workflow-designer`; multi-agent fan-out at runtime → `agenthub`.

## Pattern decision table

| Choose | When | Watch out for |
|---|---|---|
| Single agent | One bounded task, < ~5 tools | Don't add agents you don't need |
| Supervisor | Central decomposition, specialists report back | Supervisor becomes the bottleneck |
| Pipeline | Strictly sequential stages with handoffs | Rigid order; slowest stage gates throughput |
| Hierarchical | Multiple org layers, > ~8 agents | Communication overhead per level |
| Swarm | Parallel peers, fault tolerance over predictability | Hard to debug; needs consensus rules |

The planner applies this scoring deterministically — run it rather than picking by feel.

## Workflow

Each step's JSON output is the next step's design input.

### 1. Design the architecture

A requirements file needs all nine `SystemRequirements` keys (goal, description, tasks, constraints, team_size, performance_requirements, safety_requirements, integration_requirements, scale_requirements) — copy `assets/sample_system_requirements.json` and edit it:

```bash
python3 scripts/agent_planner.py requirements.json -o arch
```

Emits `arch.json` (`architecture_design`, `mermaid_diagram`, `implementation_roadmap`) plus `arch_diagram.mmd` and `arch_roadmap.json`. Read `architecture_design.pattern` and the per-agent role list; present the mermaid diagram to the user.

### 2. Generate tool schemas

Describe each agent's tools in plain JSON (copy `assets/sample_tool_descriptions.json`), then:

```bash
python3 scripts/tool_schema_generator.py tool_descriptions.json --validate -o tools
```

Emits `tools.json` (`tool_schemas`, `validation_summary`) plus provider-specific `tools_anthropic.json` / `tools_openai.json`. **Gate: every tool must print `✓ Valid`.** Fix any invalid schema before proceeding — never hand an agent an unvalidated schema.

### 3. Evaluate execution logs

Once the system runs (or against `assets/sample_execution_logs.json` for a dry run):

```bash
python3 scripts/agent_evaluator.py execution_logs.json --detailed -o eval
```

Emits `eval.json` with `summary`, `agent_metrics`, `bottleneck_analysis`, `error_analysis`, `cost_breakdown`, `sla_compliance`, and `optimization_recommendations`, plus split files (`eval_errors.json`, `eval_recommendations.json`).

### 4. Verification

The design is not done until:

1. `tool_schema_generator.py --validate` reports 0 invalid schemas.
2. `agent_evaluator.py` on a pilot run reports **0 critical issues** (the tool prints `CRITICAL: N critical issues` when found). If N > 0, apply the top item in `eval_recommendations.json`, re-run the pilot, and re-evaluate.
3. `python3 scripts/check_outputs.py` passes — each generator's output shape still matches `expected_outputs/`.

## Troubleshooting

- Planner: `Invalid requirements file … unexpected keyword argument` — the JSON is missing one of the nine required keys; diff it against `assets/sample_system_requirements.json`.
- Evaluator: `No valid execution logs found` — the input must be a JSON object with an `execution_logs` array; see `assets/sample_execution_logs.json`.

## References

- `references/agent_architecture_patterns.md` — pattern trade-offs in depth
- `references/tool_design_best_practices.md` — schema, idempotency, error-handling rules
- `references/evaluation_methodology.md` — metric definitions the evaluator implements
- `references/output_contract.md` — top-level shape of every generator's output

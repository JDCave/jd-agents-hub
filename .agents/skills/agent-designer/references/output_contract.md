# Output Contract

The top-level shape every generator emits. Downstream consumers should rely on
these section names; `scripts/check_outputs.py` fails when they drift. Without
`-o`, each generator writes exactly this JSON to stdout.

## agent_planner.py

```json
{
  "architecture_design": {
    "pattern": "supervisor | swarm | pipeline | hierarchical | single_agent",
    "agents": ["one AgentDefinition per agent"],
    "communication_topology": ["one CommunicationLink per edge"],
    "shared_resources": [],
    "guardrails": [],
    "scaling_strategy": {},
    "failure_handling": {}
  },
  "mermaid_diagram": "graph TD ...",
  "implementation_roadmap": {
    "total_duration": "estimate",
    "phases": [],
    "critical_path": [],
    "risks": [],
    "success_criteria": []
  },
  "metadata": {
    "generated_by": "agent_planner.py",
    "requirements_file": "input path",
    "architecture_pattern": "selected pattern",
    "agent_count": 0
  }
}
```

## tool_schema_generator.py

```json
{
  "tool_schemas": ["one ToolSchema per described tool"],
  "metadata": {
    "generated_by": "tool_schema_generator.py",
    "input_file": "input path",
    "tool_count": 0,
    "schema_version": "1.0"
  },
  "validation_summary": {
    "total_tools": 0,
    "total_parameters": 0,
    "total_validation_rules": 0,
    "total_examples": 0
  }
}
```

With `-o tools` and the default `--format both`, the same run also writes
`tools_openai.json` (`{"functions": [...]}`) and `tools_anthropic.json`
(`{"tools": [...]}`), plus `tools_validation.json` and `tools_examples.json`.

## agent_evaluator.py

```json
{
  "summary": {
    "evaluation_period": {"start_time": null, "end_time": null, "total_duration_hours": 0},
    "overall_health": "excellent | good | fair | poor",
    "key_findings": [],
    "critical_issues": 0,
    "improvement_opportunities": 0
  },
  "system_metrics": "PerformanceMetrics",
  "agent_metrics": {"agent-id": "PerformanceMetrics"},
  "task_type_metrics": {"task-type": "PerformanceMetrics"},
  "tool_usage_analysis": {},
  "error_analysis": ["ErrorAnalysis"],
  "bottleneck_analysis": ["BottleneckAnalysis"],
  "optimization_recommendations": ["OptimizationRecommendation"],
  "trends_analysis": {},
  "cost_breakdown": {},
  "sla_compliance": {"overall_compliant": false, "sla_details": {}, "compliance_score": 0},
  "metadata": {}
}
```

With `-o eval` and the default `--format both`, the same run also writes
`eval_summary.json`, `eval_recommendations.json`, and `eval_errors.json`.

## Field definitions

Each named dataclass above is defined in the header of its script
(`AgentDefinition` in `agent_planner.py`, `ToolSchema` in
`tool_schema_generator.py`, `PerformanceMetrics`/`ErrorAnalysis`/
`BottleneckAnalysis`/`OptimizationRecommendation` in `agent_evaluator.py`).
The dataclass fields are the authoritative contract; this page fixes the
section names a consumer can depend on.

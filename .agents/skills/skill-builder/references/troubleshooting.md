# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Gate fails "Description includes triggers" | Description lacks "Use when ..." | Second sentence must be `Use when [specific triggers]` |
| Gate fails "SKILL.md under 100 lines" | Detail accumulated in the main file | Move depth into `references/`; keep SKILL.md as the index |
| Gate fails "Consistent terminology" | Synonym pairs (skill/tool, agent/bot, user/developer) | Pick one term per concept, use it everywhere |
| Gate fails "References one level deep" | references/a.md links to references/b.md | Flatten: SKILL.md links directly to each reference |
| quality score < 90 with no FAIL rows | Dimension sub-scores (Documentation/Completeness) low | Run with `--json`, read `improvement_roadmap`, apply top item |
| security WARN on subprocess | `shell=True` usage | Use list args with `shell=False` |
| `skill_gate.py` cannot find checker | Ran from a subdirectory | Run from the repo root |

## Escalation

If a gate failure looks like a false positive (e.g. a security pattern flagged
inside a detection-tool's own pattern table), verify against the checker's
suppression convention (`# noqa: SEC-AUDITOR`) rather than bypassing the gate.

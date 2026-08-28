---
name: "skill-security-auditor"
version: "1.1.0"
license: "MIT"
when_to_use: "Before installing a skill from an untrusted source; when the gate's security check fails; when a user asks whether a skill is safe."
description: >
  Security audit and vulnerability scanner for AI agent skills before installation.
  Use when: (1) evaluating a skill from an untrusted source, (2) auditing a skill
  directory or git repo URL for malicious code, (3) pre-install security gate for
  Claude Code plugins, OpenClaw skills, or Codex skills, (4) scanning Python scripts
  for dangerous patterns like os.system, eval, subprocess, network exfiltration,
  (5) detecting prompt injection in SKILL.md files, (6) checking dependency supply
  chain risks, (7) verifying file system access stays within skill boundaries.
  Triggers: "audit this skill", "is this skill safe", "scan skill for security",
  "check skill before install", "skill security check", "skill vulnerability scan".
---

# Skill Security Auditor

Scan and audit AI agent skills for security risks before installation. Produces a
clear **PASS / WARN / FAIL** verdict with findings and remediation guidance.

## Quick Start

```bash
# Audit a local skill directory (run from the skill-security-auditor folder)
python scripts/skill_security_auditor.py /path/to/skill-name/

# Audit with strict mode (any WARN becomes FAIL)
python scripts/skill_security_auditor.py /path/to/skill-name/ --strict

# Output JSON report
python scripts/skill_security_auditor.py /path/to/skill-name/ --json
```

Exit codes: 0 = PASS, 2 = WARN (review manually), 1 = FAIL (do not install).

## What Gets Scanned

1. **Code execution risks** in `.py`/`.sh`/`.js` — command injection, `eval`/`exec`,
   obfuscation, network exfiltration, credential harvesting, privilege escalation,
   unsafe deserialization.
2. **Prompt injection** in SKILL.md and reference markdown — system-prompt override,
   role hijacking, safety bypass, hidden instructions, excessive permissions.
3. **Dependency supply chain** — typosquatting, unpinned versions, install commands
   embedded in code.
4. **File system & structure** — boundary violations, hidden files, unexpected
   binaries, symlinks pointing outside the skill.

Full pattern catalogue with severities:
[references/detection-patterns.md](references/detection-patterns.md). Threat model:
[references/threat-model.md](references/threat-model.md). Example report:
[references/sample-report.md](references/sample-report.md).

## Usage

```bash
# how to run, exit codes, and parameters
python scripts/skill_security_auditor.py --help

# scan one skill and emit JSON for the gate
python scripts/skill_security_auditor.py .agents/skills/<name> --json
```

## Troubleshooting

- **False positive on a security scanner's own patterns** — append `# noqa: SEC-AUDITOR` to the flagged line; never silence a real finding this way.
- **WARN verdict blocks nothing but nags** — review each HIGH finding with the author; use `--strict` only when you want zero tolerance.
- **Fixture in assets/ flagged** — assets/ is excluded by design; move deliberate samples there.

## Audit Workflow

1. **Run the scanner** on the skill directory or repo URL
2. **Review the report** — findings grouped by severity, each with a specific fix
3. **Verdict**: PASS = safe to install; WARN = review HIGH findings manually before installing; FAIL = do NOT install without remediation
4. **Remediate** — apply fix guidance per finding, re-run until PASS or a human signs off on each remaining WARN.

## Suppression

A line ending in `# noqa: SEC-AUDITOR` is skipped — for security tooling that
contains the dangerous-pattern strings it detects, and test fixtures. Never
silence a real finding this way.

## CI/CD Integration

Called by the skill gate at `.agents/skills/skill-tester/scripts/skill_gate.py` (security FAIL blocks the gate).
Standalone batch use:

```bash
for skill in .agents/skills/*/; do
  python .agents/skills/skill-security-auditor/scripts/skill_security_auditor.py \
    "$skill" --json >> audit-results.jsonl
done
```

## Limitations

Static analysis only — it cannot catch logic bombs or creative obfuscation with
certainty, and dependency checks use local patterns, not live CVE databases.
When in doubt after an audit, **don't install**. Ask the skill author.

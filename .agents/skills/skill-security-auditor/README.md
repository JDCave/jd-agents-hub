# skill-security-auditor

Security audit and vulnerability scanner for AI agent skills before installation.
Static analysis only — safe to run on untrusted code.

## Usage

How to run, exit codes, and all parameters:

```bash
python scripts/skill_security_auditor.py --help
```

Everyday invocations:

```bash
python scripts/skill_security_auditor.py /path/to/skill-name/          # human report
python scripts/skill_security_auditor.py /path/to/skill-name/ --json   # machine report
python scripts/skill_security_auditor.py /path/to/skill-name/ --strict # WARN becomes FAIL
```

Exit codes: 0 = PASS, 2 = WARN (review manually), 1 = FAIL (do not install).

## Example findings

```
CRITICAL [CODE-EXEC] scripts/helper.py:42
   Pattern: eval(user_input)
   Risk: Arbitrary code execution from untrusted input
   Fix: Replace eval() with ast.literal_eval() or explicit parsing
```

Each finding carries severity, category, file:line, risk, and a specific fix.
A fuller worked report: [references/sample-report.md](references/sample-report.md).

## What it scans

Code execution risks (command injection, eval/exec, obfuscation, exfiltration,
credential harvesting), prompt injection in markdown, dependency supply chain,
and file-system boundary violations. Full catalogue:
[references/detection-patterns.md](references/detection-patterns.md).

In the skill lifecycle, this scanner is invoked by the repo-root gate
(`python .agents/skills/skill-tester/scripts/skill_gate.py <skill>`); a FAIL verdict blocks commit/merge.

## Suppression

Lines ending in `# noqa: SEC-AUDITOR` are skipped — reserved for security tooling
that contains the dangerous-pattern strings it detects, and test fixtures.

## References

- [threat-model.md](references/threat-model.md) — attack vectors against agent skills
- [detection-patterns.md](references/detection-patterns.md) — complete pattern catalogue

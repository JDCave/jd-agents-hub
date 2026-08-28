# Sample audit report

Example output of `skill_security_auditor.py` on a skill that fails the gate:

```
================================================================================
  SKILL SECURITY AUDIT REPORT
  Skill: unsafe-sample
  Verdict: FAIL
================================================================================
  CRITICAL: 2    HIGH: 1    INFO: 0
================================================================================

CRITICAL [CMD-INJECT] scripts/helper.py:12
   Pattern: os.system("echo " + user_input)
   Risk: Arbitrary command execution via os.system()
   Fix: Use subprocess.run() with list arguments and shell=False

CRITICAL [CODE-EXEC] scripts/helper.py:13
   Pattern: eval(user_input)
   Risk: Arbitrary code execution from untrusted input
   Fix: Replace eval() with ast.literal_eval() or explicit parsing

HIGH [FS-BOUNDARY] scripts/scanner.py:15
   Pattern: open(os.path.expanduser("~/.ssh/id_rsa"))
   Risk: Reads SSH private key outside skill scope
   Fix: Remove filesystem access outside skill directory
```

A PASS report lists zero CRITICAL and zero HIGH findings; WARN reports need a
human sign-off on each HIGH finding before install.

#!/usr/bin/env python3
"""Run skill_review_checklist_runner on every SKILL.md in the repo + aggregate."""

import argparse
import json
import os
import subprocess
import sys

# Lives at .agents/skills/skill-tester/scripts/; repo root is 3 levels up
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# The checklist runner is a sibling skill's script — reach it via the shared
# skills root (one level above this skill), not through the repo root.
SKILLS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(SKILLS_ROOT, "skill-builder", "scripts",
                      "skill_review_checklist_runner.py")

EXCLUDE_PATTERNS = ("node_modules", ".codex", ".gemini", ".cursor",
                    ".cline", "site", ".git", "templates",
                    os.path.join("assets", "sample-skill"))


def find_skills():
    skills = []
    for root, _, files in os.walk(REPO_ROOT):
        # Normalize to forward slashes so excludes match on Windows too.
        norm = root.replace(os.sep, "/")
        if any(p.replace(os.sep, "/") in norm for p in EXCLUDE_PATTERNS):
            continue
        if "SKILL.md" in files:
            skills.append(root)
    return sorted(skills)


def audit_skill(skill_folder):
    """Run the runner; return parsed JSON result."""
    try:
        out = subprocess.run(
            [sys.executable, RUNNER, skill_folder, "--output", "json"],
            capture_output=True, text=True, timeout=10,
        )
        return json.loads(out.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        return {"error": str(e), "folder": skill_folder, "passed": 0, "total": 6, "overall": "ERROR"}


def main():
    # Parse arguments BEFORE any work: `--help` must return instantly
    # instead of running the full ~30s repo-wide audit.
    parser = argparse.ArgumentParser(
        description="Run the skill-builder review checklist on every SKILL.md "
                    "in the repo and print an aggregate report (~30s on the "
                    "full tree). Running with no arguments audits everything.",
        epilog=(
            "example:\n"
            "  %(prog)s          # audit every skill, print PASS/WARN/FAIL breakdown\n"
            "\n"
            "output: totals by verdict, failures grouped by rule, top-10 worst skills."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    skills = find_skills()
    print(f"Auditing {len(skills)} skills...\n", file=sys.stderr)

    results = []
    for i, folder in enumerate(skills, 1):
        if i % 50 == 0:
            print(f"  ... {i}/{len(skills)}", file=sys.stderr)
        results.append(audit_skill(folder))

    # Aggregate
    pass_count = sum(1 for r in results if r.get("overall") == "PASS")
    warn_count = sum(1 for r in results if r.get("overall") == "WARN")
    fail_count = sum(1 for r in results if r.get("overall") == "FAIL")
    error_count = sum(1 for r in results if r.get("overall") == "ERROR")

    # Count failures by rule
    rule_failures = {}
    for r in results:
        for check in r.get("checks", []):
            if not check.get("pass"):
                rule = check.get("rule", "unknown")
                rule_failures[rule] = rule_failures.get(rule, 0) + 1

    # Top-10 worst (most failed checks)
    worst = sorted(
        results,
        key=lambda r: (r.get("passed", 0), -len(r.get("folder", ""))),
    )[:10]

    print("=" * 72)
    print("REPO-WIDE SKILL AUDIT (skill-builder review checklist)")
    print("=" * 72)
    print(f"\nTotal SKILL.md audited: {len(results)}")
    print(f"  PASS  (6/6): {pass_count} ({100*pass_count//max(len(results),1)}%)")
    print(f"  WARN  (5/6): {warn_count}")
    print(f"  FAIL  (<=4/6): {fail_count}")
    print(f"  ERROR (couldn't parse): {error_count}")

    print("\n" + "-" * 72)
    print("FAILURES BY RULE")
    print("-" * 72)
    for rule, count in sorted(rule_failures.items(), key=lambda x: -x[1]):
        pct = 100 * count // max(len(results), 1)
        print(f"  {count:>4d} ({pct:>3d}%)  {rule}")

    print("\n" + "-" * 72)
    print("TOP-10 WORST OFFENDERS")
    print("-" * 72)
    for w in worst:
        folder = w.get("folder", "?").replace(REPO_ROOT + "/", "")
        passed = w.get("passed", 0)
        failed_rules = [c["rule"] for c in w.get("checks", []) if not c.get("pass")]
        print(f"\n  [{passed}/6] {folder}")
        for fr in failed_rules:
            print(f"    - {fr}")


if __name__ == "__main__":
    main()

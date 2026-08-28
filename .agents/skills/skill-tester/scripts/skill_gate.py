#!/usr/bin/env python3
"""skill_gate.py — the single quality gate for the skill lifecycle.

Runs every check on one skill (or all skills) and produces one verdict +
one exit code. Pre-commit and CI call THIS script, never the individual
checkers, so thresholds live in exactly one place.

Checks (in order, fail-fast per skill is NOT applied — full report first):
  1. frontmatter     skill-builder check_frontmatter.py     (per SKILL.md)
  2. name shadow     skill-builder check_skill_names.py     (repo-wide, attributed)
  3. checklist       skill-builder checklist runner         (6/6 required)
  4. structure       skill-tester skill_validator.py        (no errors, score >= 60)
  5. scripts         skill-tester script_tester.py          (overall != FAIL)
  6. quality         skill-tester quality_scorer.py         (score >= MIN_SCORE)
  7. security        skill-security-auditor                 (verdict != FAIL)

Gate policy (centralized):
  MIN_SCORE = 90       quality score must be >= 90 to pass
  Security WARN is recorded but does not block; FAIL blocks.

Usage (from repo root; the script lives inside skill-tester):
  python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>
  python .agents/skills/skill-tester/scripts/skill_gate.py --all
  python .agents/skills/skill-tester/scripts/skill_gate.py --all --json
  python .agents/skills/skill-tester/scripts/skill_gate.py --all --update-registry

Exit codes: 0 = gate passed, 1 = gate failed, 2 = usage/internal error.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# This script lives at .agents/skills/skill-tester/scripts/skill_gate.py.
# All paths resolve from its own location, so .agents stays self-contained
# (nothing inside .agents references repo-root scripts/).
_HERE = os.path.dirname(os.path.abspath(__file__))
TESTER_SCRIPTS = _HERE
SKILLS_ROOT = os.path.dirname(os.path.dirname(_HERE))       # .agents/skills
AGENTS_ROOT = os.path.dirname(SKILLS_ROOT)                  # .agents
REPO_ROOT = os.path.dirname(AGENTS_ROOT)                    # repo root
REGISTRY_PATH = os.path.join(SKILLS_ROOT, "registry.json")

BUILDER_SCRIPTS = os.path.join(SKILLS_ROOT, "skill-builder", "scripts")
AUDITOR_SCRIPT = os.path.join(SKILLS_ROOT, "skill-security-auditor", "scripts",
                              "skill_security_auditor.py")

MIN_SCORE = 90
STRUCTURE_MIN = 60  # skill_validator's own floor; gate re-checks centrally
TIMEOUT_MAP = {"script_tester": 300, "security_auditor": 120}  # others: 60s


def run_tool(args, cwd, timeout=60):
    """Run a checker; return parsed JSON dict, or {"_error": ...}."""
    try:
        proc = subprocess.run(
            [sys.executable] + args, cwd=cwd, capture_output=True,
            text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"_error": f"timeout after {timeout}s"}
    out = proc.stdout.strip()
    if out.startswith("{"):
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            pass
    return {"_error": proc.stderr.strip() or out[:500] or
            f"exit {proc.returncode} with no output"}


def find_skills():
    if not os.path.isdir(SKILLS_ROOT):
        return []
    out = []
    for entry in sorted(os.listdir(SKILLS_ROOT)):
        folder = os.path.join(SKILLS_ROOT, entry)
        if os.path.isfile(os.path.join(folder, "SKILL.md")):
            out.append(folder)
    return out


def skill_name(folder):
    return os.path.basename(os.path.normpath(folder))


# --- individual checks: each returns (status, detail) --------------------
# status: "PASS" | "FAIL" | "WARN"

def check_frontmatter(folder):
    doc = run_tool(
        [os.path.join(BUILDER_SCRIPTS, "check_frontmatter.py"),
         os.path.join(folder, "SKILL.md"), "--json"],
        cwd=REPO_ROOT,
    )
    if "_error" in doc:
        return "FAIL", {"error": doc["_error"]}
    errors = doc.get("errors", {})
    warnings = doc.get("warnings", {})
    if errors:
        return "FAIL", {"errors": errors, "warnings": warnings}
    if warnings:
        return "WARN", {"warnings": warnings}
    return "PASS", {}


def name_shadow_failures():
    """Run the repo-wide name check once; map skill folder -> messages."""
    proc = subprocess.run(
        [sys.executable, os.path.join(BUILDER_SCRIPTS, "check_skill_names.py"), "--all"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
    )
    failures = {}
    for line in proc.stdout.splitlines():
        if line.startswith("FAIL "):
            rel = line[5:].strip()
            folder = os.path.dirname(os.path.join(REPO_ROOT, rel))
            failures.setdefault(folder, []).append(line)
    return failures


def check_checklist(folder):
    doc = run_tool(
        [os.path.join(BUILDER_SCRIPTS, "skill_review_checklist_runner.py"),
         folder, "--output", "json"],
        cwd=REPO_ROOT,
    )
    if "_error" in doc:
        return "FAIL", {"error": doc["_error"]}
    overall = doc.get("overall")
    failed = [c.get("rule") for c in doc.get("checks", []) if not c.get("pass")]
    detail = {"passed": doc.get("passed", 0), "total": doc.get("total", 6),
              "failed_rules": failed}
    return ("PASS" if overall == "PASS" else "FAIL"), detail


def check_structure(folder):
    doc = run_tool(
        [os.path.join(TESTER_SCRIPTS, "skill_validator.py"), folder, "--json"],
        cwd=REPO_ROOT,
    )
    if "_error" in doc:
        return "FAIL", {"error": doc["_error"]}
    errors = doc.get("errors", [])
    score = doc.get("overall_score", 0)
    ok = not errors and score >= STRUCTURE_MIN
    return ("PASS" if ok else "FAIL"), {
        "overall_score": score, "compliance_level": doc.get("compliance_level"),
        "errors": errors,
    }


def check_scripts(folder):
    doc = run_tool(
        [os.path.join(TESTER_SCRIPTS, "script_tester.py"), folder, "--json"],
        cwd=REPO_ROOT, timeout=TIMEOUT_MAP["script_tester"],
    )
    if "_error" in doc:
        return "FAIL", {"error": doc["_error"]}
    status = doc.get("summary", {}).get("overall_status", "UNKNOWN")
    if status in ("PASS", "OK"):
        verdict = "PASS"
    elif status == "PARTIAL":
        verdict = "WARN"
    else:
        verdict = "FAIL"
    return verdict, {"overall_status": status, "summary": doc.get("summary", {})}


def check_quality(folder):
    doc = run_tool(
        [os.path.join(TESTER_SCRIPTS, "quality_scorer.py"), folder,
         "--json", "--detailed", "--include-security",
         "--minimum-score", str(MIN_SCORE)],
        cwd=TESTER_SCRIPTS,  # imports security_scorer from its own dir
    )
    if "_error" in doc:
        return "FAIL", {"error": doc["_error"]}
    score = doc.get("overall_score", 0)
    dims = {name: round(d.get("score", 0), 1)
            for name, d in doc.get("dimensions", {}).items()}
    return ("PASS" if score >= MIN_SCORE else "FAIL"), {
        "overall_score": score,
        "letter_grade": doc.get("letter_grade"),
        "min_score_required": MIN_SCORE,
        "dimensions": dims,
        "improvement_roadmap": doc.get("improvement_roadmap", [])[:5],
    }


def check_security(folder):
    doc = run_tool(
        [AUDITOR_SCRIPT, folder, "--json"],
        cwd=REPO_ROOT, timeout=TIMEOUT_MAP["security_auditor"],
    )
    if "_error" in doc:
        return "FAIL", {"error": doc["_error"]}
    verdict = doc.get("verdict", "UNKNOWN")
    counts = doc.get("summary_counts") or doc.get("counts") or {}
    findings = [{"severity": f.get("severity"), "id": f.get("id"),
                 "file": f.get("file"), "message": (f.get("message") or "")[:120]}
                for f in (doc.get("findings") or [])[:10]]
    if verdict == "PASS":
        gate_status = "PASS"
    elif verdict == "WARN":
        gate_status = "WARN"
    else:
        gate_status = "FAIL"
    return gate_status, {"verdict": verdict, "counts": counts, "findings": findings}


CHECKS = [
    ("frontmatter", check_frontmatter),
    ("checklist", check_checklist),
    ("structure", check_structure),
    ("scripts", check_scripts),
    ("quality", check_quality),
    ("security", check_security),
]

# Naming convention: skills that manage the skill lifecycle itself are
# "meta-skills" and must cluster under the skill- prefix (skill-builder,
# skill-tester, skill-security-auditor), so they are distinguishable from
# task skills (pdf-extract, csv-lint, ...) in listings and slash completion.
# Folder name and frontmatter name: must match, ^[a-z][a-z0-9-]*$, and
# meta-skills (skills whose scripts/ reference other skills' SKILL.md or
# that live alongside the lifecycle tooling) must match ^skill-[a-z-]+$.
META_NAME_RE = re.compile(r"^skill-[a-z]+(-[a-z]+)*$")


try:
    import yaml  # optional: naming check needs it; check_frontmatter gates on it
except ImportError:
    yaml = None


def check_naming_convention(folder):
    if yaml is None:
        return "FAIL", {"error": "PyYAML missing (pip install pyyaml) — cannot verify frontmatter name"}  # noqa: SEC-AUDITOR (guidance, not a command)
    folder_name = skill_name(folder)
    skill_md = os.path.join(folder, "SKILL.md")
    try:
        text = open(skill_md, encoding="utf-8").read()
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
        fm = yaml.safe_load(m.group(1)) if m else {}
        fm_name = str((fm or {}).get("name", ""))
    except (OSError, yaml.YAMLError):
        return "FAIL", {"error": f"cannot read frontmatter of {skill_md}"}

    problems = []
    if folder_name != fm_name:
        problems.append(f"folder '{folder_name}' != frontmatter name '{fm_name}'")
    if META_NAME_RE.match(folder_name):
        # meta-skill: its own name must match; nothing else to check
        pass
    else:
        # Non-meta names are allowed only outside the meta family; but skills
        # in this repo currently are all meta. Flag names that LOOK like they
        # want to be meta (reference skill_gate/registry) but don't match.
        meta_markers = ("skill_gate", "registry.json", "skill lifecycle")
        try:
            content = open(skill_md, encoding="utf-8").read().lower()
        except OSError:
            content = ""
        if any(marker in content for marker in meta_markers) and folder_name != fm_name:
            problems.append("skill references lifecycle tooling but is not named skill-*")

    return ("FAIL", {"problems": problems}) if problems else ("PASS", {})


def gate_skill(folder, shadow_failures):
    checks = {}
    for name, fn in CHECKS:
        checks[name] = fn(folder)
    msgs = shadow_failures.get(os.path.abspath(folder))
    checks["name_shadow"] = ("PASS", {}) if not msgs else ("FAIL", {"messages": msgs})
    checks["naming"] = check_naming_convention(folder)

    statuses = [s for s, _ in checks.values()]
    verdict = "FAIL" if "FAIL" in statuses else (
        "WARN" if "WARN" in statuses else "PASS")

    quality_score = checks["quality"][1].get("overall_score")
    return {
        "skill": skill_name(folder),
        "folder": os.path.relpath(folder, REPO_ROOT).replace("\\", "/"),
        "verdict": verdict,
        "quality_score": quality_score,
        "min_score_required": MIN_SCORE,
        "checks": {name: {"status": s, "detail": d}
                   for name, (s, d) in checks.items()},
    }


def update_registry(results):
    registry = {}
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, encoding="utf-8") as f:
                registry = json.load(f)
        except (json.JSONDecodeError, OSError):
            registry = {}

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for r in results:
        entry = registry.setdefault(r["skill"], {"status": "draft"})
        entry["last_gate"] = {
            "timestamp": stamp,
            "verdict": r["verdict"],
            "quality_score": r["quality_score"],
        }
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")


def print_report(results, as_json):
    if as_json:
        print(json.dumps({
            "gate": "skill-gate",
            "min_score_required": MIN_SCORE,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "results": results,
            "overall": ("PASS" if all(r["verdict"] == "PASS" for r in results)
                        else "FAIL"),
        }, indent=2, ensure_ascii=False))
        return

    icons = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}
    for r in results:
        print(f"\n{icons[r['verdict']]} {r['skill']}  "
              f"(quality {r['quality_score']}/{r['min_score_required']})")
        for name, c in r["checks"].items():
            line = f"    {icons[c['status']]} {name}"
            d = c["detail"]
            if name == "quality" and d.get("overall_score") is not None:
                line += f" — score {d['overall_score']} ({d.get('letter_grade')})"
            if name == "checklist" and d.get("failed_rules"):
                line += f" — failed: {', '.join(d['failed_rules'])}"
            if name == "frontmatter" and d.get("errors"):
                line += f" — {list(d['errors'].values())[0][0][:80]}"
            if name == "structure" and d.get("errors"):
                line += f" — {str(d['errors'][0])[:80]}"
            if name == "scripts" and d.get("overall_status"):
                line += f" — {d['overall_status']}"
            if name == "security" and d.get("verdict"):
                line += f" — {d['verdict']}"
            if name == "name_shadow" and d.get("messages"):
                line += f" — shadows built-in command"
            print(line)

    n_pass = sum(1 for r in results if r["verdict"] == "PASS")
    print(f"\n{'=' * 60}")
    print(f"GATE: {n_pass}/{len(results)} skills pass "
          f"(min score {MIN_SCORE}, security FAIL blocks)")
    for r in results:
        if r["verdict"] != "PASS":
            print(f"  BLOCKED: {r['skill']} — "
                  + ", ".join(n for n, c in r["checks"].items()
                              if c["status"] == "FAIL"))


def main():
    ap = argparse.ArgumentParser(
        description="Unified skill lifecycle quality gate. "
                    "All thresholds live here; pre-commit and CI call this.",
        epilog=(
            "example:\n"
            "  %(prog)s .agents/skills/my-skill            # one skill\n"
            "  %(prog)s --all --update-registry            # every skill, record results\n"
            "\n"
            "checks: frontmatter, name shadow, checklist (6), structure, scripts,\n"
            "quality (score >= 90), security, naming. exit 0 pass / 1 blocked."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="*",
                    help="Skill folder(s) to gate (default with --all: every skill)")
    ap.add_argument("--all", action="store_true", help="Gate every skill")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--update-registry", action="store_true",
                    help=f"Record results in {os.path.relpath(REGISTRY_PATH, REPO_ROOT)}")
    args = ap.parse_args()

    if args.all:
        folders = find_skills()
    elif args.skills:
        folders = []
        for s in args.skills:
            folder = os.path.abspath(s)
            if not os.path.isfile(os.path.join(folder, "SKILL.md")):
                print(f"error: no SKILL.md under {s}", file=sys.stderr)
                return 2
            folders.append(folder)
    else:
        ap.print_help()
        return 2

    if not folders:
        print("No skills found to gate.", file=sys.stderr)
        return 0

    shadow = name_shadow_failures()
    results = [gate_skill(f, shadow) for f in folders]

    if args.update_registry:
        update_registry(results)

    print_report(results, args.json)
    return 0 if all(r["verdict"] != "FAIL" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

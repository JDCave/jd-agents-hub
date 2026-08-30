#!/usr/bin/env python3
"""
Check Skeletons - regression check for the workflow scaffolder's templates.

With no arguments, regenerates every built-in skeleton via the scaffolder
and compares it byte-for-value against the matching file in
expected_outputs/. With file arguments, each file is validated as a
workflow spec (a JSON object with a known 'pattern' and a 'name'); files
that are not specs are skipped, not failed.

Exit codes: 0 = all checks pass, 1 = mismatch or invalid spec,
2 = usage error.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
SCAFFOLDER = SCRIPTS_DIR / "workflow_scaffolder.py"

# pattern -> expected-output file
EXPECTED = {
    "sequential": "sequential.json",
    "parallel": "parallel.json",
    "router": "router.json",
    "orchestrator": "orchestrator.json",
    "evaluator": "evaluator.json",
}


def generate(pattern: str, name: str = "new-workflow") -> Optional[Dict[str, Any]]:
    """Run the scaffolder for one pattern; return the parsed skeleton."""
    try:
        proc = subprocess.run(
            [sys.executable, str(SCAFFOLDER), pattern, "--name", name],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def check_expected(pattern: str, filename: str) -> Dict[str, Any]:
    """Regenerate one skeleton and diff it against expected_outputs/."""
    record: Dict[str, Any] = {"check": f"template:{pattern}", "status": "FAIL",
                              "problems": []}
    expected_path = SKILL_ROOT / "expected_outputs" / filename
    try:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record["problems"] = [f"cannot read {filename}: {exc}"]
        return record

    name = expected.get("name", "new-workflow")
    actual = generate(pattern, name)
    if actual is None:
        record["problems"] = [f"scaffolder failed or produced invalid JSON for '{pattern}'"]
        return record

    if actual != expected:
        record["problems"] = [f"regenerated '{pattern}' skeleton differs from {filename}"]
    else:
        record["status"] = "PASS"
    return record


def check_spec(path: str) -> Dict[str, Any]:
    """Validate one file as a workflow spec."""
    record: Dict[str, Any] = {"check": f"spec:{Path(path).name}", "status": "FAIL",
                              "problems": []}
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        record["problems"] = [f"cannot read {path}: {exc}"]
        return record
    except json.JSONDecodeError as exc:
        record["problems"] = [f"{path} is not valid JSON: {exc}"]
        return record

    if not isinstance(spec, dict) or "pattern" not in spec:
        record["status"] = "SKIP"
        record["problems"] = ["no 'pattern' key — not a workflow spec"]
        return record

    pattern = str(spec["pattern"])
    if pattern not in EXPECTED:
        record["problems"] = [f"unknown pattern '{pattern}'"]
        return record
    if not isinstance(spec.get("name"), str) or not spec.get("name"):
        record["problems"] = ["missing or empty 'name'"]
        return record
    record["status"] = "PASS"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify scaffolder templates against expected_outputs/ and validate spec files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python check_skeletons.py\n"
            "  python check_skeletons.py assets/sample_spec_parallel.json\n"
            "  python check_skeletons.py --json\n"
            "  python check_skeletons.py --help"
        ))
    parser.add_argument("paths", nargs="*",
                        help="Workflow spec file(s) to validate (default: verify all templates)")
    parser.add_argument("--json", action="store_true", help="Emit a JSON report")
    args = parser.parse_args()

    if args.paths:
        records = [check_spec(p) for p in args.paths]
    else:
        records = [check_expected(pattern, filename)
                   for pattern, filename in EXPECTED.items()]

    if args.json:
        print(json.dumps({"results": records}, indent=2))
    else:
        for record in records:
            print(f"[{record['status']}] {record['check']}")
            for problem in record["problems"]:
                print(f"        {problem}")

    failures = [r for r in records if r["status"] == "FAIL"]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

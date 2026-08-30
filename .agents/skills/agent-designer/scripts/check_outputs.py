#!/usr/bin/env python3
"""
Check Outputs - sample-input smoke check for the agent-designer generators.

Runs each generator script on its bundled sample input and compares the
output shape (top-level sections and their value kinds) against the
matching file in expected_outputs/. This automates the drift check from
SKILL.md: it fails when a script's output contract changes shape, which
is what downstream consumers rely on.

Exit codes: 0 = all checked pairs match, 1 = mismatch or script failure,
2 = usage error.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent

# (script, sample input, expected output) triples shipped with this skill.
PAIRS = [
    ("agent_planner.py", "sample_system_requirements.json",
     "sample_agent_architecture.json"),
    ("tool_schema_generator.py", "sample_tool_descriptions.json",
     "sample_tool_schemas.json"),
    ("agent_evaluator.py", "sample_execution_logs.json",
     "sample_evaluation_report.json"),
]


def run_generator(script: str, sample_path: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    """Run one generator script on a sample input; return (parsed output, error)."""
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script), str(sample_path)],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return None, f"{script} timed out after 60s"
    if proc.returncode != 0:
        return None, f"{script} exited {proc.returncode}: {proc.stderr.strip()[:200]}"
    try:
        return json.loads(proc.stdout), ""
    except json.JSONDecodeError as exc:
        return None, f"{script} stdout was not valid JSON: {exc}"


def kind_of(value: Any) -> str:
    """Human-readable JSON kind for mismatch messages."""
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return type(value).__name__


def compare_shape(expected: Any, actual: Any, path: str = "$", depth: int = 0) -> List[str]:
    """Compare container shape, not values.

    At the top level (depth 0) the section-name sets must match exactly;
    deeper levels only check value kinds, because the expected files are
    illustrative samples with different instance data.
    """
    problems: List[str] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        if depth == 0:
            for key in sorted(set(expected) - set(actual)):
                problems.append(f"{path}: missing section '{key}'")
            for key in sorted(set(actual) - set(expected)):
                problems.append(f"{path}: unexpected section '{key}'")
        for key in sorted(set(expected) & set(actual)):
            problems.extend(
                compare_shape(expected[key], actual[key], f"{path}.{key}", depth + 1))
    elif isinstance(expected, list) and isinstance(actual, list):
        if expected and actual:
            problems.extend(
                compare_shape(expected[0], actual[0], f"{path}[0]", depth + 1))
        elif expected and not actual:
            problems.append(f"{path}: expected a non-empty array, got empty")
    elif isinstance(expected, (dict, list)) or isinstance(actual, (dict, list)):
        problems.append(
            f"{path}: kind mismatch — expected {kind_of(expected)}, got {kind_of(actual)}")
    return problems


def select_pairs(paths: List[str]) -> Tuple[List[Tuple[str, Path, Path]], List[str]]:
    """Map requested paths to (script, input, expected) pairs."""
    if not paths:
        return [(s, SKILL_ROOT / "assets" / a, SKILL_ROOT / "expected_outputs" / e)
                for s, a, e in PAIRS], []
    selected, skipped = [], []
    for raw in paths:
        name = Path(raw).name
        match = [p for p in PAIRS if p[1] == name]
        if match:
            s, a, e = match[0]
            selected.append((s, SKILL_ROOT / "assets" / a, SKILL_ROOT / "expected_outputs" / e))
        else:
            skipped.append(raw)
    return selected, skipped


def check_pair(script: str, sample: Path, expected_path: Path) -> Dict[str, Any]:
    """Run one pair and return a check record for the report."""
    record: Dict[str, Any] = {"script": script, "input": sample.name, "status": "FAIL",
                              "problems": []}
    try:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record["problems"] = [f"cannot read {expected_path.name}: {exc}"]
        return record

    actual, error = run_generator(script, sample)
    if actual is None:
        record["problems"] = [error]
        return record

    problems = compare_shape(expected, actual)
    record["problems"] = problems
    if not problems:
        record["status"] = "PASS"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify generator output shape against expected_outputs/ samples.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python check_outputs.py\n"
            "  python check_outputs.py assets/sample_tool_descriptions.json\n"
            "  python check_outputs.py --json\n"
            "  python check_outputs.py --help"
        ))
    parser.add_argument("paths", nargs="*",
                        help="Sample input file(s) to check (default: all bundled pairs)")
    parser.add_argument("--json", action="store_true", help="Emit a JSON report")
    args = parser.parse_args()

    selected, skipped = select_pairs(args.paths)
    if not selected and not skipped:
        print("nothing to check", file=sys.stderr)
        return 2

    results = [check_pair(script, sample, expected)
               for script, sample, expected in selected]
    failed = [r for r in results if r["status"] != "PASS"]

    if args.json:
        print(json.dumps({"results": results, "skipped": skipped}, indent=2))
    else:
        for record in results:
            mark = "PASS" if record["status"] == "PASS" else "FAIL"
            print(f"[{mark}] {record['script']} <- {record['input']}")
            for problem in record["problems"]:
                print(f"       {problem}")
        for raw in skipped:
            print(f"[SKIP] {raw} — no expected-output pair for this file")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

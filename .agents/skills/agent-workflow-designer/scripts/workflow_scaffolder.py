#!/usr/bin/env python3
"""Generate workflow skeleton configurations from common multi-agent patterns.

Accepts either a pattern name (sequential, parallel, router, orchestrator,
evaluator) or a path to a workflow spec JSON file of the form
{"pattern": "...", "name": "..."} — the pattern choice made during design,
persisted as a file, scaffolds the matching configuration.

The skeleton is printed to stdout; pass --output to write it to a file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple


def sequential_template(name: str) -> Dict:
    return {
        "name": name,
        "pattern": "sequential",
        "steps": [
            {"id": "research", "agent": "researcher", "next": "draft"},
            {"id": "draft", "agent": "writer", "next": "review"},
            {"id": "review", "agent": "reviewer", "next": None},
        ],
        "retry": {"max_attempts": 2, "backoff_seconds": 2},
    }


def parallel_template(name: str) -> Dict:
    return {
        "name": name,
        "pattern": "parallel",
        "fan_out": {
            "tasks": ["research_a", "research_b", "research_c"],
            "agent": "analyst",
        },
        "fan_in": {"agent": "synthesizer", "output": "combined_report"},
        "timeouts": {"per_task_seconds": 180, "fan_in_seconds": 120},
    }


def router_template(name: str) -> Dict:
    return {
        "name": name,
        "pattern": "router",
        "router": {"agent": "router", "routes": ["sales", "support", "engineering"]},
        "handlers": {
            "sales": {"agent": "sales_specialist"},
            "support": {"agent": "support_specialist"},
            "engineering": {"agent": "engineering_specialist"},
        },
        "fallback": {"agent": "generalist"},
    }


def orchestrator_template(name: str) -> Dict:
    return {
        "name": name,
        "pattern": "orchestrator",
        "orchestrator": {"agent": "orchestrator", "planning": "dynamic"},
        "specialists": ["researcher", "coder", "analyst", "writer"],
        "execution": {
            "dependency_mode": "dag",
            "max_parallel": 3,
            "completion_policy": "all_required",
        },
    }


def evaluator_template(name: str) -> Dict:
    return {
        "name": name,
        "pattern": "evaluator",
        "generator": {"agent": "generator"},
        "evaluator": {"agent": "evaluator", "criteria": ["accuracy", "format", "safety"]},
        "loop": {
            "max_iterations": 3,
            "pass_threshold": 0.8,
            "on_fail": "revise_and_retry",
        },
    }


PATTERNS = {
    "sequential": sequential_template,
    "parallel": parallel_template,
    "router": router_template,
    "orchestrator": orchestrator_template,
    "evaluator": evaluator_template,
}


def resolve_request(arg: str) -> Tuple[str, str]:
    """Return (pattern, name) from a pattern name or a workflow spec file path.

    name is None unless a spec file carries one, so the caller's --name wins
    for plain pattern arguments.
    """
    if arg.endswith(".json") or Path(arg).is_file():
        spec = json.loads(Path(arg).read_text(encoding="utf-8"))
        if not isinstance(spec, dict) or "pattern" not in spec:
            raise ValueError(f"{arg}: spec file must be a JSON object with a 'pattern' key")
        return str(spec["pattern"]), spec.get("name")
    return arg, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a workflow skeleton configuration from a pattern.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python workflow_scaffolder.py sequential --name content-pipeline\n"
            "  python workflow_scaffolder.py orchestrator --name incident-triage \\\n"
            "      -o workflows/incident-triage.json\n"
            "  python workflow_scaffolder.py assets/sample_spec_parallel.json\n"
            "  python workflow_scaffolder.py --help\n"
            "patterns: " + ", ".join(sorted(PATTERNS)) +
            " — or a path to a spec JSON {\"pattern\": ..., \"name\": ...}"
        ))
    parser.add_argument("pattern",
                        help="Pattern name, or a workflow spec JSON file path")
    parser.add_argument("--name", default="new-workflow",
                        help="Workflow name (ignored when the input is a spec file)")
    parser.add_argument("-o", "--output",
                        help="Optional output path for the JSON configuration")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        pattern, spec_name = resolve_request(args.pattern)
    except FileNotFoundError as exc:
        print(f"Spec file not found: {exc}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid workflow spec: {exc}", file=sys.stderr)
        return 1

    name = spec_name if spec_name else args.name

    if pattern not in PATTERNS:
        print(f"Unknown pattern '{pattern}'. Choose one of: "
              f"{', '.join(sorted(PATTERNS))}", file=sys.stderr)
        return 1

    config = PATTERNS[pattern](name)
    payload = json.dumps(config, indent=2)

    if args.output:
        out = Path(args.output)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Cannot write {out}: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote workflow configuration to {out}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

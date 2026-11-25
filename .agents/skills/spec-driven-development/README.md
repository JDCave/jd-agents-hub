# spec-driven-development

Port of GitHub spec-kit's spec-driven-development process as one hub skill: a
durable constitution, feature specification, technical plan, task list, and
convergence pass drive implementation. The process value is the on-disk
`.specify/` artifact set, not a command-line platform: each step reads the
artifacts the previous step wrote, so intent survives sessions and reviews.

This skill is a thin router. `SKILL.md` holds the process order, the five
cross-cutting rules, and the artifact map. The detailed instructions for each
step live in flat files under `references/`, and the nine page templates plus a
few inert samples live under `assets/`. There is no `specify` CLI dependency:
the bundled standard-library script creates and resolves `.specify/` itself.

## Usage

Commands below are relative to this skill folder. Run the steps in the order
`SKILL.md` gives; clarify, checklist, and analyze are optional quality gates.

```bash
# 1. seed .specify/memory and .specify/templates once
python scripts/sdd_workflow.py --action bootstrap --json

# 2. allocate specs/NNN-slug/, write spec.md, persist .specify/feature.json
python scripts/sdd_workflow.py --action new-feature --title "add user authentication" --json

# 3. resolve the current feature paths and available design documents
python scripts/sdd_workflow.py --action prereqs --json

# 4. seed plan.md and tasks.md from the bundled page templates
python scripts/sdd_workflow.py --action plan --json
python scripts/sdd_workflow.py --action tasks --json

# 5. resolve a page template (project override first, bundled asset second)
python scripts/sdd_workflow.py --action resolve-template --template spec-template --json

# 6. summarize the workspace and the current feature
python scripts/sdd_workflow.py --action status --json

# 7. full help surface, flags, and examples
python scripts/sdd_workflow.py --help
```

Every action accepts `--json` for one stable JSON object and prints one line per
item without it. Exit 0 is success; exit 2 is bad input or a missing
prerequisite. `plan` and `tasks` refuse to overwrite an existing artifact unless
`--force` is passed. The positional target defaults to the current directory; a
file argument resolves to its parent folder, so sample files are accepted
harmlessly.

Then run the step in the conversation: read `references/command-constitution.md`
for the constitution step, `references/command-specify.md` for specify, and so
on. Read only the file for the step being run.

## Example

A fresh project, bootstrap plus a first feature:

```text
$ python scripts/sdd_workflow.py --action bootstrap --json
{"SPECIFY_DIR": ".specify", "CREATED_DIRS": [".specify/memory", ".specify/templates"], "CONSTITUTION": "created"}

$ python scripts/sdd_workflow.py --action new-feature --title "Add user authentication" --json
{"FEATURE_DIR": "specs/001-add-user-authentication", "SPEC_FILE": "specs/001-add-user-authentication/spec.md", "FEATURE_NUM": "001"}
```

The resulting tree:

```text
.specify/
├── feature.json                       {"feature_directory": "specs/001-add-user-authentication"}
├── memory/constitution.md             seeded from the bundled constitution template
└── templates/                         optional project overrides
specs/001-add-user-authentication/
└── spec.md                            seeded from the bundled spec template
```

The `--json` shapes above are recorded as real outputs in `expected_outputs/`
(`bootstrap.json`, `new-feature.json`, `prereqs.json`, `status.json`) and checked
by the unit suite.

## Layout

| Path | Purpose |
|---|---|
| `SKILL.md` | Process router: step order, cross-cutting rules, artifact map |
| `README.md` | This overview, usage, example, and verification notes |
| `references/command-constitution.md` … `command-converge.md` | One ported reference per step |
| `references/mechanisms.md` | Cross-cutting rules, `.specify/` contract, script contract |
| `references/upstream.md` | Source URL, commit pin, ported files, MIT notice, drop list |
| `assets/templates/` | Five verbatim spec-kit page templates |
| `assets/sample-*` | Inert sample request, spec, plan, feature pointer, and prereq report |
| `scripts/sdd_workflow.py` | Standard-library CLI for `.specify/` and template operations |
| `expected_outputs/` | Real `--json` outputs of documented invocations |
| `tests/test_sdd_workflow.py` | Read-only unit tests in the system temp area |

## Verification

```bash
python -m unittest discover -s tests
python scripts/sdd_workflow.py --help
python scripts/sdd_workflow.py assets/sample-feature.json
python scripts/sdd_workflow.py --action status --json
```

All four commands are expected to exit 0. The script uses only the Python
standard library, so there is no installation step and no `requirements.txt`.
The process itself is validated by the artifacts: each step checks the artifact
the previous step produced, and `analyze` plus `converge` audit the set as a
whole.

## Attribution

Process and page templates are ported from GitHub spec-kit at commit
`c43849408ac0de2ca6a52f14eaae71449776057b`, MIT licensed, Copyright GitHub, Inc.
The full provenance, modification list, and dropped CLI mechanisms are recorded
in `references/upstream.md`.

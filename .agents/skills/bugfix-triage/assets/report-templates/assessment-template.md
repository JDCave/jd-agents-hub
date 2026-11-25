# Bug Assessment: <short title>

- **Slug**: <BUG_SLUG>
- **Created**: <ISO 8601 date>
- **Source**: <URL or pasted text>
- **Verdict**: <valid | likely valid, needs reproduction | invalid>
- **Severity**: <critical | high | medium | low>

## Report (verbatim or summarized)

<Quoted or condensed report content. If a URL was fetched, include the title and a short excerpt; link the URL.>

## Symptom

<One or two sentences describing the observed behavior and the expected behavior.>

## Reproduction

1. <step>
2. <step>
3. <step>

<Mark unknowns as [NEEDS CLARIFICATION: ...] rather than guessing.>

## Suspected Code Paths

- `path/to/file.py:42` — <why this location is a candidate>
- `path/to/other.ts:func()` — <why this location is a candidate>

## Root Cause Hypothesis

<One paragraph. State confidence: high / medium / low.>

## Proposed Remediation

**Preferred**: <one or two paragraphs describing the change.>

**Alternatives** (optional):
- <alternative plus its trade-off>

**Files likely to change**:
- `path/to/file.py`
- `path/to/test_file.py`

**Tests to add or update**:
- <test description>

## Risks & Considerations

- <API breakage, migration, performance, security, observability, or other risk>

## URL Trust Record

- **URL supplied**: <verbatim URL, or "none">
- **Host**: <parsed host, or "not applicable">
- **Policy branch**: <allowlisted | confirmed-by-user | auto-refused: reason | not-applicable>

## Open Questions

- [NEEDS CLARIFICATION: <question>]

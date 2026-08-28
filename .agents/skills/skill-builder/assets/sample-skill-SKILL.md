---
name: csv-lint
description: Validate CSV files against a schema, check delimiter consistency, and report malformed rows with line numbers. Use when user mentions CSV validation, malformed spreadsheets, or schema checking.
---

# CSV Lint

## Quick start

```bash
python scripts/csv_lint.py assets/orders.csv --schema assets/schema.json
```

## Workflows

1. Load schema (column names, types)
2. Scan rows; type-check each cell
3. Report malformed rows with line numbers

## Advanced features

See [REFERENCE.md](REFERENCE.md) for custom type rules.

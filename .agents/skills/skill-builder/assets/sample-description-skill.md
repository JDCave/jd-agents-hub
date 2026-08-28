---
name: pdf-extract
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
---

# PDF Extract

## Quick start

```python
from pypdf import PdfReader
reader = PdfReader("input.pdf")
print(reader.pages[0].extract_text())
```

## Workflows

1. Extract text: iterate pages, collect text
2. Extract tables: locate table regions, parse rows
3. Merge documents: append page objects, write output

## Advanced features

See [REFERENCE.md](REFERENCE.md) for form-filling and encryption handling.

---
name: axon-ivy-external-loader
description: Use this skill when need to load, to get context from Excel (.xlsx) and BPMN (.bpmn) files.
---

## Requirements

* Python 3 on PATH (`python` or `python3`).
* load_excel.py` needs `openpyxl`; install with `pip install openpyxl`.

## Use

Use when the user or another skill points to external Excel or BPMN requirement files.

* `.xlsx` → `load_excel.py`
* `.bpmn` → `load_bpmn.py`
* Read supported text formats directly.
* Report unsupported/unreadable files as gaps.
* Read only. Never modify source files.

Input is a file, folder, or glob. Folders are not recursive. If the path does not exist or resolves to nothing, report it and stop. Never guess another path.

## Load

Only load the suitable file types from the sources run the appropriate loaders.
Pass the path exactly as given, never one you found yourself. If a loader exits with `path not found`, report that.
If missing `openpyxl`, run `pip install openpyxl` and retry once.

```bash
python <skill-dir>/loaders/load_excel.py <path> --out .external-context/excel_dump.txt
python <skill-dir>/loaders/load_bpmn.py <path> --out .external-context/bpmn_dump.txt
```

Useful options:

* Excel: `--sheet NAME`, `--max-rows N`
* BPMN: `--format flow` and `--format prose` drop content — digest from the default full output

A `.xml` file whose root element is `<definitions>` may be passed directly to the BPMN loader.

Always read the generated dump. A successful loader message is not extracted content. If a dump is too large, search/read the relevant sections and record that limitation.

## Digest

Create a factual digest for each source covering relevant structure and content such as fields, roles, rules, volumes, deadlines, SLAs, thresholds, and integrations.

Keep every fact traceable:

* Excel: file + sheet + cell/row
* BPMN: file + process/pool/lane/node

Apply these rules:

* Prefer an English `*_EN` sheet over an equivalent translated twin; do not digest both.
* Skip exporter/configuration sheets such as `Version`, `ParameterSheet`, and `ConfigItem` as business requirements.
* Account for headers below row 1 and merged section headings.
* If a formula has no cached value, report the formula; do not calculate it.
* Preserve BPMN annotations, lanes, departments, and relevant vendor fields.
* Treat numbers according to context: volume, limit, deadline, threshold, SLA, etc.
* Report contradictions; do not resolve them.
* Never infer missing content or summarise from filenames alone.

## Manifest

Write `.external-context/manifest.md` and return its content.

```markdown
# External Context Manifest

Requested: <path exactly as given>
Loaded from: <path the loaders actually read>

## Sources
| File | Type | Status | Notes |
|------|------|--------|-------|
| Process_Master.xlsx | Excel | loaded | EN sheet used |

## Digest
### Process_Master.xlsx
<facts with sheet/cell or BPMN location references>

## Findings
- Contradiction: workbook says 3 working days; BPMN note says 10 working days.

## Gaps
- Spec_v2.docx — unreadable; request a supported export.
```

Keep dumps and the manifest under `.external-context/`. They are temporary working files.

Only persist the digest elsewhere when the user explicitly asks.

When called by another skill, return the manifest and dump paths; use a subagent only when the sources are large and the caller needs only the digest.

Before returning, ensure every requested file is represented as a source or gap, every generated dump was inspected, and every extracted fact remains traceable.

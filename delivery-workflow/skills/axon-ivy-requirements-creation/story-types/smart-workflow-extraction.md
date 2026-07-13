# Story Type: Smart Workflow Extraction

**Source:** Each "Extract Data using Smart Workflow" step in the requirements.

**Count:** One story per distinct data class needing AI extraction.

**This story enables** the process to automatically extract structured data from uploaded documents or text using AI.

---

## Scope

Each story covers one extraction subprocess end-to-end: data class, schema, process file, and failure handling.

---

## Implementation Details to Include

### Part A — Data class for the subprocess

- `simpleName`, `namespace`
- Input field: file variable (`java.io.InputStream` for images, `ch.ivyteam.ivy.scripting.objects.Binary` for PDFs) or `String` for text
- Output field: the target model class (e.g., `invoice.model.Invoice`)
- Error fields: `ch.ivyteam.ivy.bpm.error.BpmError error` and `String errorStr`

### Part B — Extraction schema table

List every field the AI must extract:

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| invoiceNumber | String | Yes | e.g. INV-0001-0001 |
| invoiceDate | String | Yes | ISO format yyyy-MM-dd |
| totalDue | Double | Yes | Final amount, no currency symbol |
| items | List (wrapped) | Yes | Use wrapper class — AI cannot return List directly |

> Replace with actual fields from requirements. Use wrapper classes for any List fields.

### Part C — Subprocess process file

- Kind: `CALLABLE_SUB`
- Elements: `CallSubStart` → `Script (init)` → `ProgramInterface (AgenticProcessCall)` → `CallSubEnd`, with `ErrorBoundaryEvent` → `Script (parse error)` → `CallSubEnd`
- `resultType`: fully-qualified model class ending in `.class`
- `resultMapping`: maps to output field
- System prompt: list every field to extract with format rules
- Query template: pass file or text variable directly — e.g., `"query": "Extract invoice data:\n<%= in.uploadedFile %>"`

### Part D — Failure handling

- When extraction fails: return null, set `errorStr`, caller decides what to do
- When optional fields are missing: AI returns null, caller validates before use

---

## Acceptance Criteria

- [ ] Subprocess is callable with correct signature
- [ ] Input/output types match the data class definition
- [ ] Returns populated object when given a valid test document
- [ ] Returns null/errorStr (not an exception) when extraction fails
- [ ] All required fields extracted correctly from a sample document

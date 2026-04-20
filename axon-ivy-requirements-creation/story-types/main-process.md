# Story Type: Main Process

**Source:** Process Overview / High-Level Flow section of the requirements.

**This story enables** the system to orchestrate the end-to-end workflow from start to completion.

---

## Scope

One story for the orchestration process (the main `.p.json` file under `processes/`).

---

## Implementation Details to Include

### Process Overview

- File location (`processes/[namespace]/[ProcessName].p.json`)
- Process kind: `NORMAL` (standard process, not a callable sub)
- Schema: `https://json-schema.axonivy.com/14.0-dev/project/process.json`

### Process Variables

| Name | Type | Description |
| ---- | ---- | ----------- |
| entity | Entity class | The main domain object being processed |
| status | StatusEnum | Current process state |

### Process Flow

Document each element in order:

#### Start Element

- Element type: `RequestStart` or `CallSubStart`
- Input parameters: name, type, description
- `activatorRoles`: roles that may start this process (for RequestStart)
- Initial script: field population on entry

#### Script Steps

For each Script element:
- Purpose (e.g., "Initialize entity", "Set status to APPROVED")
- Key IvyScript lines (no lambdas, no stream API, use `as` for casting)

#### Subprocess Calls

For each CallSub element:
- Target subprocess and story reference
- Input/output mapping
- Error boundary handling

#### User Tasks

For each UserTask:

| Property | Value |
| -------- | ----- |
| Name | Task display name |
| Dialog | `src_hd/[namespace]/[DialogName]/[DialogName].xhtml` |
| Responsible roles | Role IDs from roles.yaml |
| Expiry | Duration (ISO-8601) or none |
| Expiry responsible | Role to reassign on expiry |
| Form story | Link to form-composition story |

#### Multi-Task Data Passing Pattern

When a second task needs data produced inside the first task's dialog (e.g., a UUID created on save), use a **Case custom field** — NOT `call.map`.

**Why:** `call.map` is resolved when the UserTask element is entered, before the dialog runs. The value will always be null.

**Pattern:**

1. Define the field in `config/custom-fields.yaml` under `Cases:` with `Type: STRING`
2. Write in the first task's `output.code`:
   ```
   ivy.case.customFields().stringField("fieldName").set(out.value != null ? out.value : "");
   ```
3. Read in the second task's `call.code` (never `call.map`):
   ```
   param.fieldName = ivy.case.customFields().stringField("fieldName").getOrDefault("");
   ```

The story must include:
- The `custom-fields.yaml` snippet for the Case field
- The `output.code` snippet for the producing task
- The `call.code` snippet for the consuming task

#### Gateways

For each gateway:

| Condition | Route |
| --------- | ----- |
| Approved | → Next task |
| Rejected | → End (rejected) |

#### End Elements

- Success end: name, final status set
- Failure/rejection end: name, final status set

---

## Acceptance Criteria

- [ ] Process starts without error when triggered by an authorized role
- [ ] All UserTask assignments resolve to a valid role
- [ ] Gateways route correctly for each condition
- [ ] Case custom fields are defined in `custom-fields.yaml` for any multi-task data passing
- [ ] Process reaches a defined End element for every possible execution path

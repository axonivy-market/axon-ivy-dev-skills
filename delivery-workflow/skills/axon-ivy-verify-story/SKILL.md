---
name: axon-ivy-verify-story
description: Verify story implementation by checking acceptance criteria, loading verify parts from other skills, and validating UI behavior (field interactions, disable/enable, show/hide, validations).
---

**MANDATORY**: Run this skill after implementing each story via `axon-ivy-implement-story`. This skill orchestrates all verification — both artifact-specific checks (delegated to other verify skills) and behavioral/UI checks unique to this skill.

## Verification Workflow

### Phase 1: Acceptance Criteria Check

Read the story file. For each acceptance criterion (`- [ ] ...`):
1. Verify the artifact/behavior described actually exists and works
2. Mark as passed or flag the issue

### Phase 2: Delegate to Artifact-Specific Verify Skills

Based on which files were created/modified, load and run the appropriate verify skills:

| If modified... | Load and run |
|----------------|-------------|
| Any `.p.json` file | `axon-ivy-process-verify` — run its full checklist |
| Any `cms_*.yaml` file | `axon-ivy-cms-verify` — run its full checklist |
| Any `.d.json` data class | Phase 3: Data Class Checks (below) |
| Any `.xhtml` dialog/component | Phase 4: UI Behavior Checks (below) |
| Any `.java` model/enum | Phase 3: Java Checks (below) |
| `roles.yaml` / `users.yaml` | Phase 3: Config Checks (below) |

### Phase 3: Structural Checks

#### Data Class Checks (`.d.json`)

Read each created/modified `.d.json` file and verify:

- [ ] **Field completeness** — every field from the story's field table exists with correct name, type, and comment
- [ ] **No extra fields** — no fields exist that aren't in the story specification
- [ ] **Type correctness** — field types match exactly (e.g., `java.util.Date` not `String` for dates, enum types not `String` for fixed choices)
- [ ] **Namespace matches** — the `namespace` field matches the expected package path

#### Java Checks (enum, entity, model)

- [ ] **Enum values** — all values from the story are present, no extras, correct naming convention (UPPER_SNAKE_CASE)
- [ ] **Entity fields** — all fields present with correct types and annotations
- [ ] **Repository methods** — all specified CRUD/finder methods exist
- [ ] **Serializable** — model classes implement `Serializable` if used in process data

#### Config Checks (roles, users)

- [ ] **Roles exist** — each role from the story is defined in `config/roles.yaml`
- [ ] **Role hierarchy** — parent roles match the story specification
- [ ] **Users exist** — each test user from the story exists in `config/users.yaml`
- [ ] **User role assignment** — each user has the correct role(s)

### Phase 4: UI Behavior Checks

**This is the core unique value of this skill.** Read each `.xhtml` file created/modified and verify the following categories.

---

## UI Behavior Checklist

### 4.1 Disabled/Enabled Conditions

Scan for `disabled="#{...}"` on buttons and inputs. Verify:

- [ ] **Submit/action buttons** have a disabled condition that prevents premature submission
- [ ] **Disabled conditions reference the correct data fields** — e.g., `disabled="#{empty data.inputFile}"` checks the right field
- [ ] **Conditions become satisfiable** — the field they check CAN actually be set by a prior user action on the same form
- [ ] **No dead buttons** — no button is permanently disabled because its enable condition can never be met

```xml
<!-- COMMON BUG: checking server field but only client upload populates it -->
<!-- File upload sets data.uploadedFile, NOT data.inputFile -->
<p:commandButton disabled="#{empty data.inputFile}" />  <!-- Always disabled! -->

<!-- FIX: check the field that actually gets populated, or use onchange -->
<p:commandButton disabled="#{empty data.inputFile and empty data.uploadedFile}"
                 widgetVar="submitBtn" />
<p:fileUpload onchange="PF('submitBtn').enable();" />
```

### 4.2 Rendered/Visible Conditions

Scan for `rendered="#{...}"` on panels and sections. Verify:

- [ ] **Conditional sections** show/hide based on correct data state
- [ ] **Rendered expressions are reachable** — the condition can actually become true through user interaction
- [ ] **No orphaned content** — panels that can never render (condition always false)
- [ ] **Null safety** — rendered expressions handle null data objects gracefully

```xml
<!-- COMMON BUG: rendered check on object that might be null -->
<p:panel rendered="#{data.approvalData.status == 'APPROVED'}">  <!-- NPE if approvalData is null -->

<!-- FIX: null-safe check -->
<p:panel rendered="#{not empty data.approvalData and data.approvalData.status == 'APPROVED'}">
```

### 4.3 Required Field Conditions

Scan for `required="#{...}"` (conditional required) and `required="true"`. Verify:

- [ ] **All required fields from the story** have `required="true"` or a conditional expression
- [ ] **Conditional required** — fields that become required based on another field's value have correct EL expressions
- [ ] **Required messages** — required fields have corresponding validation/error messages (via CMS or `requiredMessage`)

```xml
<!-- Example: Permit number required only when work permit is needed -->
<p:inputText value="#{data.workPermitNumber}"
             required="#{data.workPermitRequired}"
             requiredMessage="#{ivy.cms.co('.../WorkPermitNumberRequired')}" />
```

### 4.4 Update/Process Attributes

Scan `<p:commandButton>` and `<p:ajax>` for `update` and `process` attributes. Verify:

- [ ] **Buttons update the right regions** — `update="form"` or `update="@form"` or specific panel IDs
- [ ] **Process scope is correct** — `process="@form"` for full form submit, `process="@this"` for action-only buttons (like Cancel)
- [ ] **Ajax update targets exist** — every ID referenced in `update="..."` actually exists in the page
- [ ] **File uploads include enctype** — forms with file upload have `enctype="multipart/form-data"` or use PrimeFaces auto-handling

### 4.5 Data Binding Consistency

Scan all `value="#{data.*}"` bindings. Verify:

- [ ] **All bound fields exist** in the dialog's data class (`.d.json`)
- [ ] **Type compatibility** — a `<p:calendar>` binds to a `Date` field, `<p:selectOneMenu>` binds to an enum, etc.
- [ ] **No typos in field paths** — `#{data.employeData}` vs `#{data.employeeData}`
- [ ] **Nested object access is null-safe** — `#{data.approval.status}` will NPE if `approval` is null

### 4.6 Component Mode Consistency (Read-Only vs Editable)

For reusable components with a `readOnly` attribute:

- [ ] **Read-only mode** renders `<h:outputText>` or disabled inputs, NOT editable fields
- [ ] **Editable mode** renders proper input components
- [ ] **The form using the component** passes the correct mode for the current user role/task step
- [ ] **All component attributes** from the story are implemented (value, readOnly, showHeader, etc.)

### 4.7 Form Action Buttons

Verify form actions match the story specification:

- [ ] **All buttons from the story exist** (Submit, Save Draft, Approve, Reject, Cancel, etc.)
- [ ] **Button actions map to correct process events** — `actionListener="#{logic.submit}"` matches an `HtmlDialogEventStart` named "submit"
- [ ] **Confirmation dialogs** for destructive actions (Reject, Cancel) if specified in the story
- [ ] **Button order/placement** follows UI conventions (Cancel left, Submit right)

### 4.8 Layout and Responsiveness

- [ ] **Grid layout** uses PrimeFlex (`grid`, `col-12`, `col-6`, etc.)
- [ ] **Form sections** match the story's layout description (tabs, accordion, panels)
- [ ] **Labels** use CMS references, not hardcoded strings (cross-check with `axon-ivy-cms-verify`)

---

## Cross-Cutting Checks

### CMS Completeness

For every `#{ivy.cms.co('...')}` reference in the XHTML:
- [ ] The CMS key exists in ALL `cms_*.yaml` language files
- [ ] The CMS value is non-empty and meaningful

### Process ↔ Dialog Contract

For every dialog referenced by the main process:
- [ ] The `HtmlDialogStart` signature matches the `DialogCall` in the process
- [ ] Input/output mapping is consistent — fields passed in are used, results mapped back
- [ ] The dialog's `HtmlDialogEventStart` names match `actionListener="#{logic.<name>}"` in the XHTML

### Data Flow Integrity

Trace the data flow through the full story:
- [ ] Data written by one step is readable by the next step
- [ ] No data is silently lost between process steps (unmapped fields)
- [ ] Status transitions follow the state machine defined in the requirements

---

## Quick Reference: Common Bugs by Story Type

| Story Type | Most Common Bug | How to Detect |
|-----------|----------------|--------------|
| UI Component | Missing `readOnly` mode handling | Check `rendered` toggle for edit/view |
| Form | Button disabled forever | Trace disabled condition to data source |
| Form | File upload doesn't enable submit | Check if server field vs client field |
| Process | SubProcessCall uses `.` instead of `/` | `axon-ivy-process-verify` check #1 |
| CMS | `Yes`/`No` keys parsed as boolean | `axon-ivy-cms-verify` check #1 |
| Data Class | Wrong type for date fields | `String` instead of `java.util.Date` |
| Entity | Missing `Serializable` | Class used in process data without it |
| Config | Role name mismatch | Process `activator` doesn't match `roles.yaml` |

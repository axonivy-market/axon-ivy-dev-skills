# Create Implementation Stories from Requirements

Decompose the requirements document into implementation stories. Each story is saved as a separate file (`story_1.md`, `story_2.md`, ...) in `[project]/documents/stories/` — create the folder if it doesn't exist.

---

## Story Types (in dependency order)

Stories follow a layered dependency chain. Create them in this order:

```
Data Model → Entity + Repository → AI/Extractions → UI Components → Tag Library → Forms → Main Process → Roles & Config
```

### Data Model Story

**Source:** Data Classes + Enumerations sections of the requirements.

One story covering all foundational data structures:

- All enumerations (one table listing each enum and its values)
- All data classes (one section per class with field tables)
- Group fields within large data classes by logical category

**Why one story:** Data classes are small, have no logic, and are tightly interdependent.

### Entity and Repository Story

**Source:** Persist Data step + Entity definition in requirements.

One story for the persistence layer:

- Entity definition (composes data classes, adds lifecycle metadata like `createdDate`, `modifiedDate`, `status`)
- Repository class with CRUD methods (save, findById, findByStatus, findAll, delete, plus domain-specific finders)

**Why together:** A repository without its entity is not useful.

### Smart Workflow Extraction Stories

**Source:** Each "Extract Data using Smart Workflow" step in the requirements.

One story per extraction type. Each story must include:

#### Part A — Data class for the subprocess

- `simpleName`, `namespace`
- Input field: file variable (`java.io.InputStream` for images, `ch.ivyteam.ivy.scripting.objects.Binary` for PDFs) or `String` for text
- Output field: the target model class (e.g., `invoice.model.Invoice`)
- Error fields: `ch.ivyteam.ivy.bpm.error.BpmError error` and `String errorStr`

#### Part B — Extraction schema table

List every field the AI must extract:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| invoiceNumber | String | Yes | e.g. INV-0001-0001 |
| invoiceDate | String | Yes | ISO format yyyy-MM-dd |
| totalDue | Double | Yes | Final amount, no currency symbol |
| items | List (wrapped) | Yes | Use wrapper class — AI cannot return List directly |

#### Part C — Subprocess process file

- Kind: `CALLABLE_SUB`
- Elements: `CallSubStart` → `Script (init)` → `ProgramInterface (AgenticProcessCall)` → `CallSubEnd`, with `ErrorBoundaryEvent` → `Script (parse error)` → `CallSubEnd`
- `resultType`: fully-qualified model class ending in `.class`
- `resultMapping`: maps to output field
- System prompt: list every field to extract with format rules
- Query template: pass file or text variable directly — e.g., `"query": "Extract invoice data:\n<%= in.uploadedFile %>"`

#### Part D — Failure handling

- State what happens when extraction fails: return null, set `errorStr`, caller decides
- State what happens for missing optional fields: AI returns null, caller validates

**Why separate:** Each extraction has its own schema and output type, can be developed independently.

**Count:** Number of stories = number of distinct data classes needing AI extraction.

Acceptance criteria template:

- [ ] Subprocess is callable with correct signature
- [ ] Input/output types match the data class definition
- [ ] Returns populated object when given a valid test document
- [ ] Returns null/errorStr (not an exception) when extraction fails
- [ ] All required fields extracted correctly from a sample invoice

### Reusable UI Component Stories

**Source:** Form field tables from all user task steps that have forms.

This requires cross-form analysis before creating stories.

**Step 1 — Build a reuse matrix:**

List all forms, note which data sections appear in each and in what mode.

| Data Section | Form A (mode) | Form B (mode) | Form C (mode) |
| ------------ | ------------- | ------------- | ------------- |
| Section X | editable | read-only | - |
| Section Y | read-only | read-only | read-only |

Any section appearing in 2+ forms should become a reusable component.

**Step 2 — Group fields into components:**

Common groupings:

- Identity/Profile fields (names, IDs)
- Job/Position fields (title, department, dates)
- Contact fields (email, phone)
- Address fields (street, city, state, country)
- Document/ID fields (passport, national ID, SSN)
- Financial/Banking fields
- Emergency contact fields
- Approval/Status tracking fields

Each logical group = one component story.

**Each component story includes:**

- Component file location and type (Composite Component)
- Attributes table (`value`, `readOnly`, `showHeader`)
- Fields table with Type and Required columns
- Layout description
- Usage examples (read-only and editable mode)

**Count:** Number of stories = number of distinct logical field groups across all forms.

### Tag Library Registration Story

**Source:** Technical necessity (not from a business requirement).

One story to register all reusable components in a single tag library:

- Tag library XML file definition (namespace, prefix)
- List of all components to register
- Configuration updates needed

### Form Composition Stories

**Source:** Each user task step that has a form.

One story per form, composing reusable components:

- Which components are used and in what mode (read-only vs editable)
- Form layout (tabs, accordion, sections)
- Form actions (buttons: Save Draft, Submit, Approve, Reject, Return)
- Backing bean logic (initialization, validation, submission)
- Privacy: which data sections are visible to which role

**Count:** Number of stories = number of user tasks with a form.

### Main Process Story

**Source:** Process Overview / High-Level Flow section.

One story for the orchestration process:

- Process location
- Process variables (name, type, description)
- Process flow sections:
  - Start element with input parameters
  - Subprocess calls (referencing extraction stories)
  - Script steps (data initialization, status updates)
  - User tasks (referencing form stories, assignment rules, expiry, dialog references)
  - Gateways (decision routing tables)
  - End elements (success and failure paths)

### Roles and Configuration Story

**Source:** Roles and Permissions section.

One story for role definitions and test user accounts:

- Role definitions (file location, role names, descriptions)
- Test users (one per role, with credentials and role assignments)

---

## Story File Format

Each story file follows this structure:

```markdown
# Story [N]: [Title]

## Description
One-line summary of what this story delivers.

## Dependencies
List of story numbers this depends on.

## Implementation Details

### Part A: [Sub-section]
Tables, field definitions, code references...

### Part B: [Sub-section]
...

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] ...
```

---

## Decision Rules

### When to consolidate into one story

- Items are small and have no independent logic (e.g., data classes, enums)
- Items are not independently useful (e.g., entity without repository)
- Splitting would create stories too small to be meaningful

### When to split into separate stories

- Items have different input/output types (e.g., separate extraction schemas)
- Items can be developed and tested independently
- Items are assigned to different developers or teams

### When to create a technical story (not from requirements)

- Infrastructure glue is needed between layers (e.g., tag library registration)
- Cross-cutting concerns need explicit setup (e.g., security configuration)

---

## Quick Reference

| Requirements Section | Story Type | Count |
| -------------------- | ---------- | ----- |
| Data Classes + Enumerations | Data Model | 1 |
| Persist Data + Entity Definition | Entity + Repository | 1 |
| Each "Extract using Smart Workflow" step | Smart Workflow Extraction | 1 per extraction |
| Form field tables (cross-form analysis) | Reusable UI Components | 1 per field group |
| (Technical necessity) | Tag Library Registration | 1 |
| Each User Task with a form | Form Composition | 1 per form |
| Process Flow diagram | Main Process | 1 |
| Roles and Permissions | Roles + Config | 1 |

**Typical total:** `1 (data) + 1 (entity) + N (extractions) + M (components) + 1 (taglib) + K (forms) + 1 (process) + 1 (config)`

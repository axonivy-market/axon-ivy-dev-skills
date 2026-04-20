# Create Implementation Stories from Requirements

Decompose the requirements document into implementation stories. Each story is saved as a separate file in `[project]/documents/stories/` — create the folder if it doesn't exist.

**Filename convention:** `story_NN_type-name.md` — encode the story number and type in the filename so developers can navigate without opening each file.

Examples: `story_01_data-model.md`, `story_02_entity-repository.md`, `story_03_extraction-invoice.md`, `story_04_component-contact-fields.md`, `story_05_taglib.md`, `story_06_form-create-invoice.md`, `story_07_process-main.md`, `story_08_security.md`, `story_09_error-expiry.md`, `story_10_roles-config.md`

---

## Story Types (in dependency order)

Stories follow a layered dependency chain. Create them in this order:

```
Data Model → Entity + Repository → AI/Extractions → UI Components → Tag Library → Forms → Main Process → Security → Error & Expiry → Roles & Config
```

**Before generating any story of a given type, read the corresponding file in `story-types/` for full rules, required sections, and acceptance criteria:**

| Story Type | Detail File | Filename Pattern |
| ---------- | ----------- | ---------------- |
| Data Model | `story-types/data-model.md` | `story_01_data-model.md` |
| Entity + Repository | `story-types/entity-repository.md` | `story_02_entity-repository.md` |
| Smart Workflow Extraction | `story-types/smart-workflow-extraction.md` | `story_0N_extraction-[name].md` |
| Reusable UI Component | `story-types/ui-component.md` | `story_0N_component-[group].md` |
| Tag Library Registration | `story-types/taglib.md` | `story_0N_taglib.md` |
| Form Composition | `story-types/form-composition.md` | `story_0N_form-[task-name].md` |
| Main Process | `story-types/main-process.md` | `story_0N_process-main.md` |
| Security | `story-types/security.md` | `story_0N_security.md` |
| Error & Expiry | `story-types/error-expiry.md` | `story_0N_error-expiry.md` |
| Roles + Config | `story-types/roles-config.md` | `story_0N_roles-config.md` |
| Custom Technical | `story-types/custom-technical.md` | `story_0N_technical-[name].md` |

---

## Story File Format

Each story file follows this structure:

```markdown
# Story [NN]: [Title]

## User Framing
This story enables [role] to [action/goal].

## Description
One-line summary of what this story delivers.

## Dependencies
List of story numbers this story depends on.

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

| Requirements Section | Story Type | Count | Detail File |
| -------------------- | ---------- | ----- | ----------- |
| Data Classes + Enumerations | Data Model | 1 | `story-types/data-model.md` |
| Persist Data + Entity Definition | Entity + Repository | 1 | `story-types/entity-repository.md` |
| Each "Extract using Smart Workflow" step | Smart Workflow Extraction | 1 per extraction | `story-types/smart-workflow-extraction.md` |
| Form field tables (cross-form analysis) | Reusable UI Components | 1 per field group | `story-types/ui-component.md` |
| (Technical — skip if no shared components) | Tag Library Registration | 0 or 1 | `story-types/taglib.md` |
| Each User Task with a form | Form Composition | 1 per form | `story-types/form-composition.md` |
| Process Flow diagram | Main Process | 1 | `story-types/main-process.md` |
| Roles and Permissions + process files | Security | 1 per process | `story-types/security.md` |
| Failure paths + expiry deadlines | Error & Expiry | 1 per process | `story-types/error-expiry.md` |
| Roles and Permissions | Roles + Config | 1 | `story-types/roles-config.md` |
| Any unclassifiable technical need | Custom Technical | as needed | `story-types/custom-technical.md` |

**Typical total:** `1 (data) + 1 (entity) + N (extractions) + M (components) + 1 (taglib) + K (forms) + 1 (process) + 1 (security) + 1 (error-expiry) + 1 (config)`

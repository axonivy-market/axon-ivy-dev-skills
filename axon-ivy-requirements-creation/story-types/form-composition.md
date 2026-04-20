# Story Type: Form Composition

**Source:** Each user task step that has a form.

**Count:** One story per user task with a form.

**This story enables** [role] to complete [task name] via a structured form in the workflow.

---

## Scope

One story per form, composing reusable components and defining backing bean logic.

**Size guardrail:** If a form covers more than **2 logical field sections** OR more than **3 action buttons**, split into sub-stories — one per logical section or action group. A story too large for one sprint is a planning failure, not an implementation story.

---

## Implementation Details to Include

### Form Overview

- Dialog name and file location (`src_hd/[namespace]/[DialogName]/[DialogName].xhtml`)
- Backing bean class and location (`src/[namespace]/bean/[BeanName].java`)
- Process dialog reference (which `.p.json` dialog calls this form)
- Linked process story (which UserTask this form belongs to)

### Components Used

| Component | Mode | Source Story |
| --------- | ---- | ------------ |
| ContactFields | editable | story_04_component-contact-fields.md |
| AddressFields | read-only | story_05_component-address-fields.md |

### Layout

Describe the layout structure:
- Single page / tabs / accordion
- Section headers
- Column layout (e.g., 2-column grid using PrimeFlex)

### Form Actions

| Button Label | Action | Validation | Notes |
| ------------ | ------ | ---------- | ----- |
| Save Draft | `#{bean.saveDraft()}` | None | Saves without submitting |
| Submit | `#{bean.submit()}` | Required fields | Triggers process continuation |
| Cancel | `#{logic.close}` | None | Discards changes |

### Backing Bean Logic

- Initialization: what data is loaded in `@PostConstruct`
- Validation: rules beyond required-field checks
- Submission: what is saved, what process output is set
- No lambdas — use plain for-loops

### Privacy / Role Visibility

| Section | Visible to Role A | Visible to Role B |
| ------- | ----------------- | ----------------- |
| Contact | Yes (editable) | Yes (read-only) |
| Internal Notes | No | Yes (editable) |

---

## Acceptance Criteria

- [ ] All required fields show a validation message on submit without a value
- [ ] Save/submit writes data to the repository
- [ ] Bean has no lambda usage (use plain for-loops)
- [ ] All labels use CMS keys — no hardcoded strings
- [ ] Read-only fields cannot be edited by the user
- [ ] Form renders without error for both new and existing entities

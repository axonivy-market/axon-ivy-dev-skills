# Story Type: Reusable UI Component

**Source:** Form field tables from all user task steps that have forms.

**Count:** One story per distinct logical field group that appears in 2+ forms.

**This story enables** UI developers to build shared form components once and reuse them across multiple task forms.

---

## Pre-work: Build a Reuse Matrix

Before creating these stories, analyse all forms in the process:

| Data Section | Form A (mode) | Form B (mode) | Form C (mode) |
| ------------ | ------------- | ------------- | ------------- |
| Section X | editable | read-only | — |
| Section Y | read-only | read-only | read-only |

Any section appearing in **2+ forms** becomes a reusable component story. Sections appearing only once stay inside their form story.

**Skip the entire component layer** if no section appears in 2+ forms. Skip the Tag Library story too.

---

## Common Field Groupings

- Identity/Profile fields (names, IDs)
- Job/Position fields (title, department, dates)
- Contact fields (email, phone)
- Address fields (street, city, state, country)
- Document/ID fields (passport, national ID, SSN)
- Financial/Banking fields
- Emergency contact fields
- Approval/Status tracking fields

---

## Implementation Details to Include

- Component file location (`src_hd/[namespace]/components/[ComponentName].xhtml`) and type (Composite Component)
- Attributes table:

| Attribute | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| value | Data class | Yes | Bound data object |
| readOnly | Boolean | No (default: false) | Controls edit vs read mode |
| showHeader | Boolean | No (default: true) | Show/hide section header |

- Fields table: Field Name | Type | Required | Label CMS Key
- Layout description (grid columns, grouping)
- Usage examples:
  - Editable mode: `<comp:ContactFields value="#{bean.contact}" readOnly="false" />`
  - Read-only mode: `<comp:ContactFields value="#{bean.contact}" readOnly="true" />`

---

## Acceptance Criteria

- [ ] Component renders correctly in both `readOnly=true` and `readOnly=false` modes
- [ ] All required fields are visible and correctly bound
- [ ] Component is registered in the tag library (covered by Tag Library story)
- [ ] No hardcoded labels — all text uses CMS keys

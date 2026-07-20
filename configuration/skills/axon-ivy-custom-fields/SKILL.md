---
name: axon-ivy-custom-fields
description: Define custom fields in custom-fields.yaml for tasks, cases, and process starts, and localize their labels, descriptions, categories, and values into multiple languages via CMS entries. Use when working with custom metadata on workflow elements, or when translating custom-field text into other languages.
---

## When to Use

- Creating TaskSwitchEvent or RequestStart elements that need custom metadata
- Displaying business context in Portal widgets
- You get NullPointerException about missing custom field types
- Translating custom-field labels, descriptions, categories, or values into other languages

## Auto-Detect Type

- Working with TaskSwitchEvent → Load `task.md`
- Working with RequestStart case config → Load `case.md`
- Working with RequestStart start config → Load `start.md`
- Translating/localizing field labels or values into other languages → Load `localization.md`

## Configuration Location

`<project>/config/custom-fields.yaml`

## Data Types

- `STRING` — Short text (names, IDs, status) < 255 chars
- `TEXT` — Long text (comments, descriptions, notes)
- `NUMBER` — Numeric values (amounts, counts, percentages)
- `TIMESTAMP` — Date and time values (due dates, completion dates)

## YAML Structure

```yaml
# yaml-language-server: $schema=https://json-schema.axonivy.com/14.0-dev/config/custom-fields.json

CustomFields:
  Tasks:
    fieldName:
      Label: Display Label
      Description: Purpose of this field
      Type: STRING
      Category: Optional Category
      Hidden: false
  Cases:
    # same structure as Tasks
  Starts:
    # same structure as Tasks
```

## Critical Rules

- Field names: camelCase, no spaces (e.g., `employeeName`)
- **All fields MUST be defined before using them in processes**
- Use consistent indentation (2 or 4 spaces, no tabs)
- Choose correct types: NUMBER for numbers, TIMESTAMP for dates

## Troubleshooting

### NullPointerException Error

```text
Cannot invoke "...FieldTypeSchema.name()" because "...CustomFieldSchema.type()" is null
```

**Solution**: Add missing field definitions to `custom-fields.yaml` with `Type` specified

### Field Not Visible in Portal

**Check**: Field not marked `Hidden: true`, value is non-null, Portal widget configured correctly

## Best Practices

1. **Define before use** — Always define in YAML before referencing in process
2. **Use categories** — Group related fields for Portal organization
3. **Choose correct types** — NUMBER for numbers, TIMESTAMP for dates
4. **Clear labels** — User-friendly display text
5. **Mark technical fields hidden** — Use `Hidden: true` for integration fields

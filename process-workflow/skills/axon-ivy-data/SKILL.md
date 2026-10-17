---
name: axon-ivy-data
description: Use this skill whenever working with Axon Ivy data classes (.d.json files)
---

Use `ivy-json-files` for JSON structure and schema-validation rules. This skill covers Axon Ivy data-class semantics.

### The PERSISTENT modifier — survives a task save point

`PERSISTENT` matters for ordinary **process data**, not just JPA entities. A **UserTask (and any wait/signal) is a save point**: Ivy persists the process data there and restores it when the step resumes. A field **without** `PERSISTENT` is **dropped to null** across that save point.

Big object should not be PERSISTENT because the task's serialized data will consume a lot of memory. We should minimalistic with persisting data, only set it when really needed. Alternatively, we can use a database or the Axon Ivy business data repository (see persistence skills) to store the data and only persist the ID in the process data.

Any field whose value must still be present *after* a UserTask (e.g. a result object the task's dialog will display) needs `"modifiers": ["PERSISTENT"]`; a custom-type field also needs its Java type to `implement Serializable`.

```json
{ "name": "inviteResult", "type": "com.example.InviteResult", "modifiers": ["PERSISTENT"] }
```

**Symptom of a missing flag:** the value is correct in a Script/log right up to the UserTask, then null in the task's dialog — and it looks like a broken mapping, but the mapping is navigating a null.

## Field Type Reference

| Type | JSON value | Notes |
|------|-----------|-------|
| String | omit `"type"` (default) | Text, IDs, dates returned by AI |
| Boolean | `"Boolean"` | true/false flags |
| Integer | `"java.lang.Integer"` | Whole numbers, quantities |
| Double | `"java.lang.Double"` | Prices, amounts, rates |
| BigDecimal | `"java.math.BigDecimal"` | High-precision financial calculations |
| Date | `"ch.ivyteam.ivy.scripting.objects.Date"` | Calendar date |
| DateTime | `"ch.ivyteam.ivy.scripting.objects.DateTime"` | Full timestamp |
| Binary | `"ch.ivyteam.ivy.scripting.objects.Binary"` | Uploaded file content held in process data |
| File | `"java.io.File"` | Uploaded file handle |
| InputStream | `"java.io.InputStream"` | File content stream (for AI extraction) |
| List of objects | `"List<com.example.Item>"` | Use fully-qualified type name |
| List of strings | `"List<String>"` | Simple string lists |
| Nested object | `"com.example.Address"` | Use fully-qualified class name |
| Enum | `"com.example.Status"` | Use fully-qualified enum name |

**Double vs BigDecimal:** Use `Double` for display and simple calculations. Use `BigDecimal` only for strict financial rounding requirements.

**Dates from AI extraction:** Prefer `String` (AI returns ISO format strings). Parse to a date type in a Script element only when needed for business logic comparisons.

## Regenerate Data Classes

Call `new_axon_ivy_data_class` to regenerate Axon Ivy data classes.

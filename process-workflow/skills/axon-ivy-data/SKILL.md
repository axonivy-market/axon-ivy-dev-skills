---
name: axon-ivy-data
description: Use this skill whenever working with Axon Ivy data classes (.d.json files)
---

## Schema

**MANDATORY**: See `schema.json` in this skill folder for full JSON schema reference.

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

**Dates:** use the Ivy types above. `java.time.*` is not on the business-data persistence whitelist — on anything `Ivy.repo()` stores it risks data recovery, and `validateProject` only reports it as Information, so it ships silently.

**Custom enums** trigger the same whitelist advisory and it is unavoidable — expect it, ignore it.

## .d.json Example

One example covering a nested object, a plain string field, a comment, and a list field:

```json
{
  ...
  "fields" : [ {
    "name" : "candidate",
    "type" : "hr.hiring.model.Candidate",
    "modifiers" : [ ],
    "comment" : "The candidate being processed"
  }, {
    "name" : "status",
    "modifiers" : [ ]
  }, {
    "name" : "approved",
    "type" : "Boolean",
    "modifiers" : [ ]
  }, {
    "name" : "tasks",
    "type" : "List<hr.hiring.model.Task>",
    "modifiers" : [ ]
  } ]
}
```

## After Modifying Data Classes

**MANDATORY**: After creating or modifying any `.d.json` file, run Maven build to regenerate the Java source classes:

```bash
mvn clean install -f <project-directory>/pom.xml
```

This will compiles the data class definitions so they are available at runtime. Without this step, the process engine will not see the updated fields.

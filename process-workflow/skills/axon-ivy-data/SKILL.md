---
name: axon-ivy-data
description: Rules and patterns for Axon Ivy data classes (.d.json files).
---

## When to Use

- Creating or editing `.d.json` data class files (master data for processes or dialogs)
- Adding fields to an existing data class
- Setting up the data layer for a new workflow process

## Use Together With

- `axon-ivy-workflow-guide` - Step-by-step workflow creation
- `axon-ivy-process` - For process that uses these data classes

## After Modifying Data Classes

**MANDATORY**: After creating or modifying any `.d.json` file, run Maven build to regenerate the Java source classes:

```bash
mvn clean install -f <project-directory>/pom.xml
```

This generates the corresponding Java classes in `src_dataClasses/` (for dialog data) or compiles the data class definitions so they are available at runtime. Without this step, the process engine will not see the updated fields.

## Data Class Types

| Type | Location | Purpose |
|------|----------|---------|
| Master Data | `dataclasses/` | Workflow state container |
| Dialog Data | `src_dataClasses/` | Auto-generated UI bindings |

## .d.json Schema

See `schema.json` in this skill folder for full JSON schema reference.

**Required fields:** `simpleName`, `namespace`

**Field properties:** `name` (required), `type`, `modifiers`, `comment`, `annotations`

**Modifiers:** `PERSISTENT`, `ID`, `GENERATED`, `NOT_NULLABLE`, `UNIQUE`, `NOT_UPDATEABLE`, `NOT_INSERTABLE`, `VERSION`

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
| LocalDate | `"java.time.LocalDate"` | Date only (yyyy-MM-dd) |
| LocalDateTime | `"java.time.LocalDateTime"` | Full timestamp |
| File | `"java.io.File"` | Uploaded file handle |
| InputStream | `"java.io.InputStream"` | File content stream (for AI extraction) |
| List of objects | `"List<com.example.Item>"` | Use fully-qualified type name |
| List of strings | `"List<String>"` | Simple string lists |
| Nested object | `"com.example.Address"` | Use fully-qualified class name |
| Enum | `"com.example.Status"` | Use fully-qualified enum name |

**Double vs BigDecimal:** Use `Double` for display and simple calculations. Use `BigDecimal` only for strict financial rounding requirements.

**Dates from AI extraction:** Prefer `String` (AI returns ISO format strings). Parse to `LocalDate` in a Script element only when needed for business logic comparisons.

## .d.json Examples

### Basic Master Data

```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/data-class.json",
  "simpleName" : "OnboardingData",
  "namespace" : "hr.onboarding",
  "fields" : [ {
    "name" : "onboarding",
    "type" : "hr.onboarding.model.Onboarding",
    "modifiers" : [ ]
  }, {
    "name" : "status",
    "modifiers" : [ ]
  } ]
}
```

### With Comments

```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/data-class.json",
  "simpleName" : "HiringData",
  "namespace" : "hr.hiring",
  "fields" : [ {
    "name" : "candidate",
    "type" : "hr.hiring.model.Candidate",
    "modifiers" : [ ],
    "comment" : "The candidate being processed"
  }, {
    "name" : "approved",
    "type" : "Boolean",
    "modifiers" : [ ]
  } ]
}
```

### With List Type

```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/data-class.json",
  "simpleName" : "ProjectData",
  "namespace" : "project.management",
  "fields" : [ {
    "name" : "tasks",
    "type" : "List<project.model.Task>",
    "modifiers" : [ ]
  }, {
    "name" : "notes",
    "type" : "List<String>",
    "modifiers" : [ ]
  } ]
}
```

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

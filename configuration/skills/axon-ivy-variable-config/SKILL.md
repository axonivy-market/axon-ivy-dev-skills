---
name: axon-ivy-variable-config
description: Provide information and rules for Axon Ivy variables configurations. Use when working with Axon Ivy variable.
---

## When to Use

- Adding or editing entries in `config/variables.yaml`
- Configuring application settings (API URLs, feature flags, credentials)
- Setting up JSON-type variables with external `.json` files
- Setting up enum-restricted or time-of-day variables

## Configuration Files

`config/variables.yaml` : Environment variables

## Type Annotations

Variables default to `String`. To use a different type, add a YAML comment annotation directly above the variable entry. These are the only annotations that exist — anything not listed here is plain `String`:

| Annotation | Type | Example Value |
|------------|------|---------------|
| *(none)* | String (default) | `My Application` |
| `#[password]` | Password (encrypted at rest, hidden in UI) | `${decrypt:...}` |
| `# [file: json]` | JSON file reference | `""` (actual value lives in a separate `.json` file) |
| `# [enum: value1, value2, ...]` | Enum (restricted to the listed values) | `simulation` |
| `# [daytime]` | Time of day (`HH:MM`) | `07:00` |

The annotation comment **must** appear on the line directly above the variable entry. There is no `value:` nesting — the annotation sits directly above the key holding the value.

Description comments (plain, non-annotation comments) may span multiple lines — each line is just another `#` comment line stacked directly above the variable. The type annotation, if any, still must be the single line immediately above the variable key.

Note: the IDE writes `#[password]` without a space after `#`, while `file:`, `enum:`, and `daytime` annotations are written with a space (`# [...]`). Match this exactly when hand-editing — it reflects what the Axon Ivy IDE editor itself generates.

## variables.yaml

```yaml
# yaml-language-server: $schema=https://json-schema.axonivy.com/14.0-dev/config/variables.json
Variables:
  # Name of your application. Will be displayed on the welcome screen.
  # And this note can have many lines.
  # And one more.
  # And one more.
  AppName: My Application
  # Business API configuration.
  Api:
    # API password. Keep it secret. Never commit it to a repository.
    #[password]
    Secret: ${decrypt:laHoSeZdDWkl1rWs0DiVkw==}
    # Number of retries for the business API
    MaxRetries: "3"
    # Operation mode of the API client.
    # [enum: simulation, production]
    RunMode: simulation
  # Some kind of business config stuff.
  BusinessConfiguration:
    # Complex rules for accounting logic. Saved in a separate JSON file.
    # [file: json]
    AccountingRules: ""
    # Start time of the working day used for some calculations
    # [daytime]
    WorkdayStartTime: 07:00
```

Note that `MaxRetries` has no annotation and is a quoted string `"3"` — it is a plain `String`, not a number. Axon Ivy variables have no dedicated numeric type; store numeric-looking values as strings and parse them in code if needed.

## JSON Variable Folder Structure

For JSON-type variables (`# [file: json]`), create a `variables` folder under `config/` that mirrors the YAML nesting:

```text
config/
├── variables.yaml
└── variables/
    └── BusinessConfiguration/          # Matches "BusinessConfiguration:" section
        └── AccountingRules.json        # BusinessConfiguration.AccountingRules
```

### JSON File Example

**`BusinessConfiguration/AccountingRules.json`**:

```json
{
  "rules": [
    {"id": "R1", "name": "Approval Threshold", "condition": {"field": "amount", "operator": ">", "value": 10000}, "action": "requireApproval"},
    {"id": "R2", "name": "Duplicate Invoice", "condition": {"match": ["vendorId", "amount", "date"]}, "action": "flagForReview"},
    {"id": "R3", "name": "Period Lock", "condition": {"field": "periodStatus", "operator": "==", "value": "closed"}, "action": "blockPosting"}
  ]
}
```

The JSON structure itself is free-form — it just needs to be valid JSON matching whatever your process code expects.

## Variable Access in Code

```java
// Access variables in Java/IvyScript
String appName = Ivy.var().get("AppName");
String runMode = Ivy.var().get("Api.RunMode");

// In EL expressions
#{ivy.var.AppName}
#{ivy.var.Api.RunMode}
```

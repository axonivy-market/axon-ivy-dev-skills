---
name: axon-ivy-variable-config
description: Provide information and rules for Axon Ivy variables configurations. Use when working with Axon Ivy variable.
---

## When to Use

- Adding or editing entries in `config/variables.yaml`
- Configuring application settings (API URLs, feature flags, credentials)
- Setting up JSON-type variables with external `.json` files

## Configuration Files

`config/variables.yaml` : Environment variables

## Type Annotations

Variables default to `String`. To use a different type, add a YAML comment annotation:

| Annotation | Type | Example Value |
|------------|------|---------------|
| *(none)* | String (default) | `"My Application"` |
| `# [type: Integer]` | Integer | `3` |
| `# [type: Password]` | Password (encrypted, hidden in UI) | `"secret-value"` |
| `# [file: json]` | JSON file reference | `""` (value in separate `.json` file) |

The annotation comment **must** appear on the line directly above the `value:` entry.

## variables.yaml

```yaml
Variables:
  # String (default type)
  AppName: "My Application"

  # Integer
  MaxRetries:
    # [type: Integer]
    value: 3

  # Password (encrypted, hidden in UI)
  Api:
    Secret:
      # [type: Password]
      value: "secret-value"

  # JSON file reference
  Portal:
    # [file: json]
    Dashboard: ""

    # Nested JSON in subfolder
    Processes:
      # [file: json]
      ExternalLinks: ""
```

## JSON Variable Folder Structure

For JSON-type variables, create a `variables` folder under `config/`:

```text
config/
├── variables.yaml
└── variables/
    └── Portal/                    # Matches "Portal:" section
        ├── Dashboard.json         # Portal.Dashboard
        └── Processes/             # Nested namespace
            └── ExternalLinks.json # Portal.Processes.ExternalLinks
```

### JSON File Examples

**Empty array** (`Portal/Processes/ExternalLinks.json`):

```json
[]
```

**Complex configuration** (`Portal/Dashboard.json`):

```json
[
  {
    "id": "default-dashboard",
    "version": "13.0.0",
    "titles": [
      { "locale": "en", "value": "Dashboard" }
    ],
    "widgets": []
  }
]
```

## Variable Access in Code

```java
// Access variables in Java/IvyScript
String appName = Ivy.var().get("AppName");
String apiUrl = Ivy.var().get("Api.BaseUrl");

// In EL expressions
#{ivy.var.AppName}
#{ivy.var.Api.BaseUrl}
```

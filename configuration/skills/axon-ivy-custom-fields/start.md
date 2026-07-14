# Start Custom Fields

Define fields under `Starts:` section to attach metadata to process start events for Portal discovery and navigation.

## Process Integration

In RequestStart (`.p.json`):

```json
{
  "type": "RequestStart",
  "config": {
    "start": {
      "customFields": [
        { "name": "processCategory", "value": "\"HR Onboarding\"" },
        { "name": "requiredRole", "value": "\"HRManager\"" },
        { "name": "complexity", "value": "\"Medium\"" },
        { "name": "estimatedTime", "value": "30" }
      ]
    }
  }
}
```

## Value Expressions

Most start fields use static literal values:

```json
// Using literals (most common for start fields)
{ "name": "processCategory", "value": "\"HR Onboarding\"" }
{ "name": "requiredRole", "value": "\"HRManager\"" }
{ "name": "complexity", "value": "\"Medium\"" }

// Using static values
{ "name": "estimatedTime", "value": "30" }
{ "name": "version", "value": "\"2.0\"" }

// Using session info
{ "name": "initiatedBy", "value": "ivy.session.getUserName()" }
```

## Common Categories

- **Classification** — process category, type, business area
- **Security** — required roles, access levels, permissions
- **Metadata** — complexity, version, status
- **Context** — region, department, compliance scope
- **Information** — descriptions, instructions, prerequisites
- **Portal** — groups, display order, icons
- **Workflow** — requires approval, SLA hours, priority
- **Technical** — API enabled, integration points (usually Hidden)

## Example

```yaml
CustomFields:
  Starts:
    processCategory:
      Label: Process Category
      Description: Category for Portal organization
      Type: STRING
      Category: Classification

    requiredRole:
      Label: Required Role
      Description: Role required to start this process
      Type: STRING
      Category: Security

    estimatedTime:
      Label: Estimated Time
      Description: Estimated completion time in minutes
      Type: NUMBER
      Category: Metadata

    description:
      Label: Description
      Description: Detailed process description
      Type: TEXT
      Category: Information

    apiEnabled:
      Label: API Enabled
      Description: Can be started via API
      Type: STRING
      Category: Technical
      Hidden: true
```

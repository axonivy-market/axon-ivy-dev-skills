# Case Custom Fields

Define fields under `Cases:` section to attach business metadata to case records.

## Process Integration

In RequestStart (`.p.json`):

```json
{
  "type": "RequestStart",
  "config": {
    "case": {
      "name": "Onboarding: <%= param.employeeName %>",
      "customFields": [
        { "name": "caseType", "value": "\"Employee Onboarding\"" },
        { "name": "businessUnit", "value": "param.department" },
        { "name": "estimatedCost", "value": "5000.00" },
        { "name": "createdBy", "value": "ivy.session.getUserName()" }
      ]
    }
  }
}
```

## Value Expressions

```json
// Using literals
{ "name": "caseType", "value": "\"Employee Onboarding\"" }

// Using parameters
{ "name": "businessUnit", "value": "param.department" }

// Using session info
{ "name": "createdBy", "value": "ivy.session.getUserName()" }

// Using calculations
{ "name": "estimatedCost", "value": "param.baseCost * 1.15" }

// Using conditionals
{ "name": "priority", "value": "param.amount > 10000 ? \"High\" : \"Normal\"" }

// Using dates
{ "name": "targetDate", "value": "java.time.LocalDate.now().plusDays(30)" }
```

## Common Categories

- **Classification** — case type, category, severity
- **Organization** — business unit, department, region
- **Financial** — costs, budget, cost center
- **Audit** — created by, modified by, owner
- **Planning** — durations, estimates, targets
- **KPIs** — SLA status, satisfaction scores, completion rates
- **Dates** — milestones, deadlines, completion dates
- **Integration** — external system IDs (usually Hidden)

## Example

```yaml
CustomFields:
  Cases:
    caseType:
      Label: Case Type
      Description: Type of HR case
      Type: STRING
      Category: Classification

    businessUnit:
      Label: Business Unit
      Description: Business unit associated with this case
      Type: STRING
      Category: Organization

    estimatedCost:
      Label: Estimated Cost
      Description: Estimated cost in dollars
      Type: NUMBER
      Category: Financial

    targetDate:
      Label: Target Date
      Description: Target completion date
      Type: TIMESTAMP
      Category: Dates

    externalSystemId:
      Label: External System ID
      Description: Reference ID in external HR system
      Type: STRING
      Category: Integration
      Hidden: true
```

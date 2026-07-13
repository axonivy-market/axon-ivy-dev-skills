# Task Custom Fields

Define fields under `Tasks:` section to attach business metadata to task instances.

## Process Integration

In TaskSwitchEvent (`.p.json`):

```json
{
  "type": "TaskSwitchEvent",
  "config": {
    "task": {
      "name": "Review Employee Info",
      "customFields": [
        { "name": "employeeName", "value": "in.employee.name" },
        { "name": "department", "value": "in.employee.department" },
        { "name": "status", "value": "in.record.status.getLabel()" },
        { "name": "priority", "value": "in.isUrgent ? \"High\" : \"Normal\"" }
      ]
    }
  }
}
```

## Value Expressions

```json
// Using variables
{ "name": "employeeName", "value": "in.employee.name" }

// Using enum labels
{ "name": "status", "value": "in.status.getLabel()" }

// Using literals
{ "name": "taskType", "value": "\"HR Review\"" }

// Using conditionals
{ "name": "priority", "value": "in.isUrgent ? \"High\" : \"Normal\"" }

// Null safety
{ "name": "department", "value": "in.dept != null ? in.dept : \"Unassigned\"" }
```

## Common Categories

- **Employee Information** — employee details
- **Organization** — department, business unit, location
- **Workflow** — status, stage, priority
- **Dates** — due dates, completion dates
- **Review** — comments, approver information
- **Financial** — amounts, costs
- **Metrics** — percentages, counts, scores

## Example

```yaml
CustomFields:
  Tasks:
    employeeName:
      Label: Employee Name
      Description: Name of the employee being onboarded
      Type: STRING
      Category: Employee Information

    department:
      Label: Department
      Description: Employee's department
      Type: STRING
      Category: Organization

    startDate:
      Label: Start Date
      Description: Employee start date
      Type: TIMESTAMP
      Category: Dates

    completionPercentage:
      Label: Completion %
      Description: Task completion percentage
      Type: NUMBER
      Category: Metrics

    externalId:
      Label: External ID
      Description: Reference in external system
      Type: STRING
      Category: Integration
      Hidden: true
```

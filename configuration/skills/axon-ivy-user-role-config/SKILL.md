---
name: axon-ivy-user-role-config
description: Provide format for Axon Ivy users/roles configurations. Use when working with Axon Ivy users/roles.
---

## When to Use

- Defining or modifying roles in `config/roles.yaml`
- Adding test users in `config/users.yaml`
- Setting up role hierarchy for task assignment in workflows

## Configuration Files

`config/roles.yaml` : Role hierarchy and permissions
`config/users.yaml` : User definitions

## Role Hierarchy Semantics

- Every role implicitly inherits from `Everybody` (the root).
- A user with role `HR` can perform tasks assigned to `HR` **and** to `Everybody`.
- A user with a child role (e.g., `Recruiter` under `HR`) can perform tasks assigned to `Recruiter`, `HR`, and `Everybody`.
- The `SYSTEM` role is built-in — used for programmatic/trigger-based tasks. Do **not** define it in `roles.yaml`.

## Naming Conventions

- **Role names**: PascalCase, no spaces (e.g., `ProjectManager`, `HRAdmin`, `Recruiter`)
- **User names**: camelCase or snake_case (e.g., `pmUser`, `hr_admin`)
- Role `Id` values in `roles.yaml` must match **exactly** with:
  - `responsible.roles` in process elements (`TaskSwitchEvent`, `UserTask`)
  - `ROLE_FROM_ATTRIBUTE` script expressions
  - User `Roles:` assignments in `users.yaml`

## Schema

- `roles.yaml` schema: `https://json-schema.axonivy.com/14.0-dev/config/roles.json`
- `users.yaml` schema: `https://json-schema.axonivy.com/14.0-dev/config/users.json`

Both `Roles` and `Users` are **arrays** (not maps). All field names are **PascalCase**.

## roles.yaml

```yaml
# yaml-language-server: $schema=https://json-schema.axonivy.com/14.0-dev/config/roles.json
Roles:
  - Id: HR
    Name: HR Department
    Parent: Everybody
  - Id: Manager
    Name: Manager
    Parent: Everybody
  - Id: Recruiter
    Name: Recruiter
    Parent: HR
  - Id: ProjectManager
    Name: Project Manager
    Parent: Manager
```

Fields:
- `Id` (**required**) — unique role identifier, used in process `responsible.roles` and user `Roles`
- `Name` — display name shown in the portal
- `Parent` — parent role id (defaults to `Everybody` if omitted)
- `Members` — array of child role ids (alternative to setting `Parent` on children)

## users.yaml

```yaml
# yaml-language-server: $schema=https://json-schema.axonivy.com/14.0-dev/config/users.json
Users:
  - Name: pmUser
    FullName: Project Manager
    Password: pmUser
    Mail: pm@example.com
    Roles:
      - HR
      - ProjectManager
```

Fields:
- `Name` (**required**) — unique username for login
- `FullName` — display name
- `Password` — plain text test password
- `Mail` — email address
- `Roles` — array of role `Id` values from `roles.yaml`

## Mapping Roles to Process Tasks

When assigning a task to a role in a process element:

```json
"responsible": {
  "roles": ["HR"]
}
```

Or dynamically from process data:

```json
"responsible": {
  "type": "ROLE_FROM_ATTRIBUTE",
  "script": "in.roleName"
}
```

Ensure the role name string matches a role defined in `roles.yaml`.

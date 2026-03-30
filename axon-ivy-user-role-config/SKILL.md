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
- **User names**: snake_case (e.g., `pm_user`, `hr_admin`)
- Role names in `roles.yaml` must match **exactly** with:
  - `responsible.roles` in process elements (`TaskSwitchEvent`, `UserTask`)
  - `ROLE_FROM_ATTRIBUTE` script expressions
  - User `roles:` assignments in `users.yaml`

## roles.yaml

```yaml
Roles:
  # Parent roles
  Everybody:
  HR:
    parent: Everybody
  Manager:
    parent: Everybody

  # Child roles
  Recruiter:
    parent: HR
  ProjectManager:
    parent: Manager
```

## users.yaml

```yaml
Users:
  pm_user:
    fullName: Project Manager
    password: pm_user
    email: pm@example.com
    roles:
      - HR
      - ProjectManager
```

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

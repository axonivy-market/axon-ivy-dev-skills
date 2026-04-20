# Story Type: Roles and Configuration

**Source:** Roles and Permissions section of the requirements.

**This story enables** each role to be assigned tasks and enables testers to log in with representative accounts.

---

## Scope

One story per module. Covers `roles.yaml`, `users.yaml`, and any module-level `custom-fields.yaml` entries.

---

## Implementation Details to Include

### roles.yaml

File location: `config/roles.yaml`

Schema: `https://json-schema.axonivy.com/14.0-dev/config/roles.json`

Rules:
- `Roles` is an **array** (not a map)
- Field names are **PascalCase**: `Id`, `Name`, `Parent`
- `Id` must exactly match what process files use in `responsible.roles` and `activatorRoles`

```yaml
Roles:
  - Id: PurchasingManager
    Name: Purchasing Manager
  - Id: Buyer
    Name: Buyer
    Parent: PurchasingManager
```

Role table:

| Id | Name | Parent | Description |
| -- | ---- | ------ | ----------- |
| PurchasingManager | Purchasing Manager | — | Approves suppliers |
| Buyer | Buyer | PurchasingManager | Registers suppliers |

### users.yaml

File location: `config/users.yaml`

Schema: `https://json-schema.axonivy.com/14.0-dev/config/users.json`

Rules:
- `Users` is an **array** (not a map)
- Field names are **PascalCase**: `Name`, `FullName`, `Mail`, `Password`, `Roles`
- One test user per role minimum

```yaml
Users:
  - Name: pm.test
    FullName: PM Test User
    Mail: pm.test@example.com
    Password: pm.test
    Roles:
      - PurchasingManager
  - Name: buyer.test
    FullName: Buyer Test User
    Mail: buyer.test@example.com
    Password: buyer.test
    Roles:
      - Buyer
```

---

## Acceptance Criteria

- [ ] Each role `Id` matches exactly what process files reference in `responsible.roles`
- [ ] Every role has at least one test user
- [ ] All users have a `Mail` field set
- [ ] `roles.yaml` and `users.yaml` use array format with PascalCase field names (per schema)
- [ ] Logging in as each test user and starting the relevant process succeeds

# Story Type: Security

**Source:** Roles and Permissions section + each UserTask and RequestStart in the process.

**This story enables** process owners to verify that only authorized roles can access each task and start the process.

---

## Scope

One story per process. Does not duplicate the Roles & Config story — it focuses on *enforcement* (process-level wiring), not *definition* (config files).

---

## Implementation Details to Include

### RequestStart Permission

- Process file location
- `activatorRoles`: list the role IDs that may trigger the process
- Verify each listed role is defined in `roles.yaml`

### UserTask Role Assignments

| UserTask Name | Responsible Roles | Defined in roles.yaml? |
| ------------- | ----------------- | ---------------------- |
| Register Supplier | Buyer | ✅ |
| Approve Supplier | PurchasingManager | ✅ |

### Negative Test Scenarios

Define at least one negative test per task:
- User with role X attempts task assigned to role Y → should be denied

---

## Acceptance Criteria

- [ ] Every `UserTask` has at least one `responsible.roles` entry
- [ ] Every role listed in any process file is defined in `roles.yaml`
- [ ] `RequestStart` has the correct `activatorRoles` configured
- [ ] A user with no matching role cannot claim or complete any task
- [ ] A user with the correct role can see and complete the task

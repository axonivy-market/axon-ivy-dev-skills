# Process Script Code Patterns

Rules and patterns for writing scripts in Axon Ivy process elements.

## Critical Rules

### Data Access

**IMPORTANT**: In Script elements, you CANNOT use `param`. Use `in` instead.

- `param.*` — Only available in RequestStart element signatures (input parameters)
- `in.*` — Available in all Script elements (process data fields)
- `out.*` — For setting output values in script code

```java
// WRONG - param is not available in Script elements
String name = param.employeeName;

// CORRECT - use in to access data fields
String name = in.employeeName;
```

## Type Casting

Use the `as` keyword to cast objects:

```java
// WRONG - Java-style cast is not supported
Invoice invoice = (Invoice) in.resultObject;

// CORRECT - use 'as' keyword for casting
Invoice invoice = in.resultObject as Invoice;
```

## Common Patterns

### Initialize Entity from Data Fields

```java
import com.example.model.Employee;
import com.example.repository.EmployeeRepository;

Employee employee = new Employee();
employee.setName(in.employeeName)
        .setDepartment(in.department)
        .setId(in.employeeId);

EmployeeRepository.getInstance().create(employee);
in.employee = employee;
```

### Conditional Logic with Mock Data

```java
String employeeId = in.mockEmployeeId != null ? in.mockEmployeeId : in.employeeId;
String employeeName = in.mockEmployeeName != null ? in.mockEmployeeName : in.employeeName;

in.processedId = employeeId;
in.processedName = employeeName;
```

### Update Entity

```java
import com.example.repository.EmployeeRepository;

in.employee.setStatus("ACTIVE");
in.employee.setLastModified(java.time.LocalDateTime.now());
EmployeeRepository.getInstance().update(in.employee);
```

### Set Case/Task Metadata

```java
ivy.case.name = "Employee: " + in.employee.getName();
in.employee.setCaseId(ivy.case.getId());
```

### Access Case/Task UUID

`ivy.case` and `ivy.task` are **properties**, not method calls. `uuid()` already returns `String` — no `.toString()` needed.

```java
// WRONG — ivy.case is not a method
String caseUuid = ivy.case().uuid().toString();

// CORRECT
String caseUuid = ivy.case.uuid();
String taskUuid = ivy.task.uuid();
```

### Session, User, and Roles

Use `Ivy.session()` for the current session and role checks. The `IUser` interface does **not** expose `isMemberOf(IRole)` — calling it produces a compile error. Use `ivy.session.hasRole(...)` instead.

```java
import ch.ivyteam.ivy.security.IRole;
import ch.ivyteam.ivy.security.IUser;

// CORRECT — role check via the session
boolean isManager = ivy.session.hasRole("Manager");
IRole role = ivy.wf.getApplication().getSecurityContext().findRole("TeamLead");
boolean isLead = ivy.session.hasRole(role);

// WRONG — IUser has no isMemberOf(IRole) overload
IUser user = ivy.session.getSessionUser();
boolean isMember = user.isMemberOf(role);  // does not compile
```

**CRITICAL — `IWorkflowSession` requires method-call syntax for the user name.** IvyScript's property shortcut (`x.foo` → `x.getFoo()`) does NOT apply to `getSessionUserName()`. Calling `ivy.session.sessionUserName` produces `Field sessionUserName not found for class IWorkflowSession`. Always use the explicit `()` form.

```java
// WRONG — property syntax not supported here
String user = ivy.session.sessionUserName;

// CORRECT — explicit method call
String user = ivy.session.getSessionUserName();
IUser sessionUser = ivy.session.getSessionUser();
```

### Application reference — `IApplication.current()`

`Ivy.wf().getApplication()` is **deprecated** since 9.4 and marked for removal. Use the static factory `IApplication.current()` instead — available since 9.1.

```java
import ch.ivyteam.ivy.application.IApplication;

// WRONG — deprecated
IApplication app = ivy.wf.getApplication();

// CORRECT
IApplication app = IApplication.current();
app.getBusinessCalendarSettings();
```

### Logging

```java
ivy.log.info("Processing employee: " + in.employee.getName());
ivy.log.debug("Employee ID: " + in.employee.getId());
ivy.log.error("Failed to process: " + exception.getMessage());
```

### Date and Time Handling

```java
in.currentDate = java.time.LocalDate.now();
in.currentDateTime = java.time.LocalDateTime.now();
in.startDate = java.time.LocalDate.now().plusDays(7);
in.endDate = java.time.LocalDate.now().plusMonths(1);
```

### Boolean Flags

```java
in.isValid = in.employee.getEmail() != null && !in.employee.getEmail().isEmpty();
in.isComplete = in.employee.getStatus().equals("COMPLETED");
in.requiresReview = in.employee.getScore() < 50;
```

**CRITICAL — Use `true`/`false` literals, NOT `Boolean.TRUE`/`Boolean.FALSE`.** IvyScript does not support static field access on `java.lang.Boolean`. Writing `Boolean.TRUE` produces `Field TRUE not found for class Boolean`. Auto-boxing converts the primitive `true`/`false` to a `Boolean` field automatically.

```java
// WRONG — static field access not supported
in.approved = Boolean.TRUE;
in.rejected = Boolean.FALSE;

// CORRECT — primitive literals, auto-boxed
in.approved = true;
in.rejected = false;
```

Note: `Boolean.TRUE.equals(...)` is fine in *Java* code (e.g., managed beans), but NOT inside `.p.json` script blocks.

## RequestStart Input Mapping

In RequestStart elements, map `param` to `in` fields:

```json
"input": {
  "map": {
    "in.employeeId": "param.employeeId",
    "in.employeeName": "param.employeeName"
  }
}
```

After mapping, use `in.*` in subsequent Script elements.

## Key Reminders

1. **Never use `param` in Script elements** — it's only for RequestStart signatures
2. **Always use `in.*`** to access process data fields (use `in1.*` inside `TaskSwitchEvent` expressions)
3. **Import classes** at the top of script code
4. **Save to repository** after creating or updating entities
5. **Use `as` keyword** for type casting, not Java-style `(Type)` cast
6. **Use `true`/`false` literals**, not `Boolean.TRUE`/`Boolean.FALSE`
7. **The `obj.property` shortcut needs a full read/write JavaBean property (getter *and* setter) or a public field.** A **getter-only** property is NOT resolved and throws `Field foo not found for class …` — this includes derived getters (`customer.getFullName()` — no backing field) and plain read-only getters (a field with a getter but no setter), as well as `IWorkflowSession` (`ivy.session.getSessionUserName()`). Call the getter explicitly with `()` (e.g. `in.customer.getFullName()`, `in.bean.getCreatedApplication()`), or add a setter to make it a full property. (JSF EL in XHTML *does* resolve read-only getters, so `#{customer.fullName}` works in a dialog — this only bites in process/IvyScript expressions, and only Designer catches it, not `mvn`.)

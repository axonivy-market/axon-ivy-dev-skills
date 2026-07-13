# Ivy.repo() Verification Checklist

**MANDATORY**: Run this checklist after creating or modifying any entity or repository class that uses `Ivy.repo()`. Fix any violations before considering the task done.

## Checklist

### 1. Process Scripts — Always assign save() result back to variable

When calling repository `save()` from process scripts, always assign the result back to the variable. `Ivy.repo().save()` returns the updated entity (with ID assigned if it's a new record).

```
WRONG — not capturing updated entity:
  OnboardingRequestRepository.getInstance().save(in.request);
  // in.request might not have the generated ID

RIGHT — capture the updated entity:
  in.request = OnboardingRequestRepository.getInstance().save(in.request);
  // in.request now has the latest state including generated ID
```

### 2. Entity constructors — Only initialize child collections/objects

Entity constructors should only initialize child collections or nested objects, never set the main entity fields like `id`.

```
RIGHT — only init child objects:
  public OnboardingRequest() {
    this.employeeInfo = new EmployeeInfo();
    this.personalInfo = new PersonalInfo();
    this.approvalInfo = new ApprovalInfo();
    // Do NOT set this.id here
  }
```

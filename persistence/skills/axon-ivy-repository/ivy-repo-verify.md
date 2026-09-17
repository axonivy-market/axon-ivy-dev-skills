# Ivy.repo() Verification Checklist

**MANDATORY**: Run this checklist after creating or modifying any entity or repository class that uses `Ivy.repo()`. Fix any violations before considering the task done.

## Checklist

### 1. Process Scripts — Always assign save() result back to variable

When calling the repository from process scripts, always assign the result back to the variable. The repository method returns the saved entity with its generated ID. `Ivy.repo().save()` itself returns a `BusinessDataInfo<T>` — the repository class unwraps it with `getId()` and `find(id, Entity.class)`.

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

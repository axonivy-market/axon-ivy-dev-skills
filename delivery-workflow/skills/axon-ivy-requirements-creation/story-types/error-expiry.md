# Story Type: Error & Expiry

**Source:** Process flow steps that can fail (AI extractions, external calls) + any UserTask with an expiry deadline.

**This story enables** the operations team to handle failures gracefully without manual intervention.

---

## Scope

One story per process. Covers all failure paths and task deadlines in a single story so error handling is consistent and complete.

---

## Implementation Details to Include

### BpmError Catch Paths

For each element that can throw (subprocesses, external calls, AI extractions):

| Element | Error Type | Catch Action | End State |
| ------- | ---------- | ------------ | --------- |
| ExtractInvoice | BpmError | Script: set status = FAILED, set errorMsg | TaskEnd (failed) |
| CallExternalAPI | BpmError | Script: set status = ERROR | TaskEnd (error) |

Rules:
- Every BpmError catch path must lead to a defined End element (not a dead end in the process)
- Status field on the entity must be updated before the End element
- The user-facing error message must be a CMS key — never a hardcoded string

### UserTask Expiry Configuration

For each UserTask that has a deadline:

| UserTask | Expiry Duration | Expiry Responsible | Expiry Action |
| -------- | --------------- | ------------------ | ------------- |
| Approve Supplier | P3D (3 days) | PurchasingManager | Reassign to manager |
| Review Invoice | PT8H (8 hours) | FinanceStaff | Escalate |

### CMS Error Messages

List each error message that needs a CMS key:

| CMS Key | English Text | Used In |
| ------- | ------------ | ------- |
| error.extraction.failed | "Document extraction failed. Please try again." | ExtractInvoice catch |
| error.approval.expired | "Approval deadline exceeded. Task has been reassigned." | Approve expiry |

---

## Acceptance Criteria

- [ ] Each `BpmError` catch path leads to a defined end state (not a dead end)
- [ ] Each UserTask with an expiry has a `timeout` and `timeout.responsible` configured
- [ ] Expiry paths update entity status before ending the process
- [ ] All error messages are CMS-managed (no hardcoded strings in error dialogs)
- [ ] Triggering a deliberate failure (e.g., passing an invalid document) shows the correct error to the user

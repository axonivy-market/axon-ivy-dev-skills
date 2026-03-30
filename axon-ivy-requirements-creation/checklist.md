# Requirements Verification Checklist

Go through each category below. For every question, check if it has been answered — from the user's input, from Step 1 expansion, or by reasonable inference. Mark as N/A if not applicable to this process.

---

## Process Trigger & Input

- [ ] What triggers this process? (manual, API, scheduled, event?)
- [ ] Who can initiate it? (role, any user, system?)
- [ ] What is the input format? (text, form, file, API payload?)
- [ ] Duplicate handling — can it be triggered multiple times for the same entity?

## Process Flow

- [ ] All steps listed from start to finish
- [ ] Conditional branches identified (if X then Y, otherwise Z)
- [ ] Parallel steps identified (if any)
- [ ] Backward flows defined (send back for revision, reopen)
- [ ] Loops defined (retry, request-more-info cycles)
- [ ] All possible end states listed (completed, rejected, cancelled, failed)

## State Machine

- [ ] All statuses defined as an enumeration
- [ ] Valid transitions between statuses documented
- [ ] Each transition mapped to a trigger (user action, system event, timeout)

## Data Model

- [ ] Primary entity identified (the "thing" flowing through the process)
- [ ] All fields have: name, data type, required/optional, validation rules
- [ ] Fields grouped into logical entities/data classes
- [ ] Sub-entities or related records identified (e.g., line items, addresses)
- [ ] System-generated fields included (id, createdDate, modifiedDate, status)
- [ ] Field sources defined (user-entered, extracted, system-generated, pre-populated)

## Enumerations

- [ ] Every fixed-choice field has an explicit enum with ALL values listed
- [ ] Considered "Other" / "Not Applicable" options where appropriate

## Roles & Permissions

- [ ] All roles listed with descriptions
- [ ] Each human step has an assigned role
- [ ] Role assignment logic defined (static role, dynamic by field, by department?)
- [ ] Data visibility per role defined (who sees what, read-only vs editable)
- [ ] Actions per role defined (approve, reject, return, delegate, escalate)

## Task Configuration

- [ ] Each human task has a name, priority, and deadline/SLA
- [ ] Timeout behavior defined (escalate, auto-action, reminder)
- [ ] Unavailability handling (delegation, backup role)

## Forms & UI

- [ ] Each user task has its form sections defined
- [ ] Read-only vs editable sections per role
- [ ] Dynamic behavior documented (show/hide based on field values)
- [ ] Form actions defined (Submit, Save Draft, Approve, Reject, etc.)
- [ ] Conditional required fields documented

## Business Rules

- [ ] Validation rules for each field documented
- [ ] Ordering constraints stated (step A before step B)
- [ ] Time-based rules stated (deadlines, SLAs, business days)
- [ ] Conditional routing rules stated (e.g., "amount > X goes to VP")
- [ ] Derived/calculated values defined

## Notifications

- [ ] Each state transition has notifications defined (or explicitly marked as none)
- [ ] Recipients identified for each notification
- [ ] Channel defined (email, in-app, SMS)
- [ ] Overdue reminders defined
- [ ] Escalation notifications defined

## Integration & Persistence

- [ ] Storage defined (Axon Ivy Business Data, external DB, etc.)
- [ ] External systems listed with direction (inbound/outbound) and purpose
- [ ] Error handling for integrations (retry, fallback, manual intervention)
- [ ] Audit trail requirements defined

## Exception Handling

- [ ] Rejection paths defined at each approval step
- [ ] Cancellation rules (who can cancel, what happens to in-progress tasks)
- [ ] Automated step failure handling (retry, fallback)
- [ ] Timeout/escalation at each human step

## File Handling

> Skip if the process does not involve file uploads.

- [ ] Accepted file types defined (whitelist: e.g., PDF, PNG, JPEG)
- [ ] Maximum file size defined
- [ ] Single vs. multiple file upload defined
- [ ] File storage location defined (temp during process vs. persistent)
- [ ] File cleanup policy defined (when are temp files deleted?)
- [ ] Download/preview of uploaded file needed?
- [ ] Upload failure handling defined (retry, notify user?)

## Data Extraction / AI

> Skip if the process does not use AI or Smart Workflow extraction.

- [ ] Input document format defined (PDF, image, text, email?)
- [ ] Full extraction schema defined: every field with name, type, required/optional
- [ ] Low-confidence or missing field handling defined (null, manual review, reject?)
- [ ] Extraction failure handling defined (retry, fallback to manual entry, notify?)
- [ ] Post-extraction validation rules defined (format, range, business rules)
- [ ] Notifications for extraction events defined ("complete", "failed", "needs review")

## Security & Compliance

- [ ] Sensitive/PII data fields identified
- [ ] Data handling rules for sensitive fields (masking, encryption)
- [ ] Compliance requirements noted (if any)
- [ ] Data retention rules (if any)

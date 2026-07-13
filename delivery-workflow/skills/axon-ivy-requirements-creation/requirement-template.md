# Axon Ivy Requirement Template (Enterprise)

## 1. General Information

**Requirement ID:**
REQ-PRC-XXX

**Requirement Name:**
Short, clear name of the process

**Business Domain:**
(HR / Finance / Sales / Operations / ICT)

**Stakeholders:**
- Business Owner:
- Process Owner:
- IT Owner:

**Priority:**
Must / Should / Nice

**Status:**
Draft / Approved / Implemented

---

## 2. Business Goal

Describe **why** this process exists.

- Business problem:
- Expected outcome:
- Success metrics (KPI):

Example:
Reduce employee onboarding time from 5 days to 1 day.

---

## 3. Process Overview

### 3.1 Process Trigger

How does the process start?

- Manual start
- API call
- Scheduled
- Event from external system

### 3.2 High-Level Flow

Describe main stages.

1. Request submission
2. Manager approval
3. Processing
4. Completion

### 3.3 State Machine

Define all possible statuses and valid transitions between them.

```
STATUS_A → STATUS_B → STATUS_C → STATUS_D (end)
                ↓
           STATUS_E (end)
```

| From Status | To Status | Triggered By |
|-------------|-----------|-------------|
| DRAFT | SUBMITTED | Requester submits |
| SUBMITTED | APPROVED | Manager approves |
| SUBMITTED | REJECTED | Manager rejects |

### 3.4 Process End States

- Completed
- Rejected
- Cancelled
- Failed

---

## 4. Actors & Roles

| Role | Responsibility | Permissions |
|------|---------------|------------|
| Requester | Create request | Create / View |
| Manager | Approve or reject | Approve |
| Admin | Monitor process | View / Reassign |

---

## 4A. File Upload Specification

> Remove this section if the process does not involve file uploads.

- **Accepted file types:** (e.g., PDF, PNG, JPEG — define whitelist explicitly)
- **Maximum file size:** (e.g., 10 MB)
- **Single or multiple files:**
- **Storage location:** (temp during process / persisted to path / stored in CMS)
- **Download / preview after upload:** Yes / No
- **Upload failure handling:** (retry prompt / notify user / cancel process?)

---

## 5. Detailed Task Definition

> Repeat this section for each task in the process.

### Task: [Task Name]

**Type:**
User Task / Service Task / Script / Integration

**Responsible Role:**

**Inputs:**
- Field name
- Source

**Outputs:**
- Decision
- Updated data

**UI Required:**
Yes / No

**Validation Rules:**

**Possible Outcomes:**
- Approve
- Reject
- Request rework

---

## 5A. Data Extraction / AI Specification

> Remove this section if the process does not use AI or Smart Workflow extraction.

- **Input format:** (uploaded PDF / image / free text / email body)
- **Extraction schema:**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| invoiceNumber | String | Yes | Unique invoice identifier |
| invoiceDate | String | Yes | ISO format yyyy-MM-dd |
| totalDue | Double | Yes | Final amount due |
| items | List\<InvoiceItem\> | Yes | Line items (wrapped list) |

- **Low-confidence / missing field handling:** (return null / flag for manual review / reject submission)
- **Extraction failure handling:** (retry once / fallback to manual entry / notify user)
- **Post-extraction validation rules:** (e.g., totalDue > 0, invoiceDate is valid date)

---

## 6. Data Model

### 6.1 Enumerations

Define all fields that have a fixed set of values.

| Enum Name | Values | Used By |
|-----------|--------|---------|
| Status | DRAFT, SUBMITTED, APPROVED, REJECTED | Request entity |
| Priority | LOW, MEDIUM, HIGH, CRITICAL | Request entity |

### 6.2 Process Data

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| | | | |

### 6.3 Business Entities (Persistent)

| Entity | Purpose |
|--------|---------|
| | |

### 6.4 Data Ownership

Who can modify which data at which stage?

| Data Section | Creator | Step: [Name] | Step: [Name] | Step: [Name] |
|-------------|---------|-------------|-------------|-------------|
| | | Read-only / Editable / Hidden | | |

---

## 7. Business Rules

List important rules.

- Approval required if amount > 1000 USD
- Only HR can modify employee contract

---

## 8. Notifications

| Event | Recipient | Channel | Message Summary |
|-------|-----------|---------|----------------|
| Request submitted | Manager | Email | New request pending approval |
| Request approved | Requester | Email | Your request has been approved |
| Task overdue | Assignee + Escalation | Email | Immediate action required |

---

## 9. Integration & External Systems

| System | Direction | Purpose |
|--------|-----------|---------|
| SAP | Outbound | Create employee |
| Email Server | Outbound | Send notification |
| CRM | Inbound | Receive request |

**Error Handling:**

- Retry policy
- Manual intervention
- Compensation action

---

## 10. Exception & Alternative Flows

- Rejection path
- Timeout handling
- Escalation rules
- Rework loop

Example:
If manager does not respond within 48 hours → escalate to director.

---

## 11. SLA & Time Constraints

| Task | Due Time | Escalation |
|------|----------|------------|
| Approval | 2 days | Notify supervisor |

---

## 12. Security & Data Protection

- Sensitive/PII data fields and handling rules
- Data masking or encryption requirements
- Data visibility rules (who can see what beyond role-based task access)
- Data retention and deletion policies

---

## 13. Audit & Compliance

Must be logged:

- Who started process
- Who approved/rejected
- Timestamp history
- Data changes

---

## 14. Reporting & Monitoring

Required dashboards:

- Active cases
- Overdue tasks
- Throughput
- Processing time

---

## 15. UI Requirements

> Repeat this section for each form/dialog in the process.

### Form: [Form Name]

**Used by role:**
**Purpose:**

| Section | Fields | Mode |
|---------|--------|------|
| | | Read-only / Editable |

**Dynamic behavior:**
(show/hide rules, conditional fields)

**Form actions:**
(buttons: Submit, Save Draft, Approve, Reject, etc.)

---

## 16. Versioning & Change Impact

- Impact on running cases
- Migration needed?
- Backward compatibility

---

## 17. Acceptance Criteria

Process is accepted when:

- All main flow works
- Exception paths handled
- SLA enforced
- Integration tested
- Audit logs available

---

## 18. Traceability

| Requirement | Process | Task | Test Case |
|-------------|---------|------|-----------|
| REQ-PRC-001 | | | TC-01 |

---

## 19. Open Questions / Risks

- Missing integration specification
- Undefined SLA
- Pending legal approval

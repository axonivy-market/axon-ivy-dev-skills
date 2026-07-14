# Thinking Dimensions for Requirements Expansion

Use these dimensions to expand vague user input into detailed requirements. Not every process needs every dimension — pick what applies.

---

## Identify the Workflow Skeleton

Extract the sequential steps from the user's description.

Ask yourself:

- What triggers this process?
- What are the major steps from start to finish?
- Who is involved at each step?
- What are the possible endings?

**Example:** *"Customers submit complaints, support triages them, then the team resolves them"* becomes:

```
Submit Complaint → Triage (Support) → Assign to Team → Resolve → Close
```

---

## Decompose Each Step

For every step, answer: What goes in? What comes out? What can go wrong?

```
Any Step
├── Input: What data or artifact enters this step?
├── Output: What data or decision comes out?
├── Rules: What constraints apply?
├── Errors: What happens when things fail?
└── Actor: Who or what performs this step? (human role, system, external service)
```

**The key question:** If I were coding this step RIGHT NOW, what would I need to know?

---

## Define the Data Model

Every piece of data mentioned must have a type, a name, and a home.

- List every noun/field mentioned across all steps
- Group them into logical entities
- For each field, determine: data type, required or optional, validation rules, source (user-entered, extracted, system-generated)
- Create the composite entity that ties everything together

**Example:** User says *"invoice details"* — that's vague. Unpack it: invoice number, vendor name, amount, currency, due date, line items, tax amount, PO reference... Each needs a type and validation rule.

**Critical insight:** Vague terms like "details", "info", "data" always explode into many specific fields when you think about what the user actually needs to capture.

---

## Define Enumerations and Controlled Values

Any field with a fixed set of values needs an explicit enumeration.

**How to spot them:** If a field's answer is "one of these options" rather than free text, it's an enum.

**Examples across domains:**

- Priority → Low, Medium, High, Critical
- Leave Type → Annual, Sick, Unpaid, Parental, Bereavement
- Payment Method → Credit Card, Bank Transfer, Cash, Check
- Approval Status → Pending, Approved, Rejected, Returned

Always consider: Do you need an "Other" option? A "Not Applicable"?

---

## Define Roles, Permissions, and Task Assignment

Who does what, and what can they see/do?

For each human step, define:

- WHO is assigned the task (by role, by username, dynamically by some field?)
- WHAT they can see (read-only vs editable fields)
- WHAT actions they can take (approve, reject, return, delegate, escalate)
- WHEN they must complete it (deadline, SLA)
- WHAT PRIORITY the task has

**Example:** *"Manager approves"* → WHICH manager? The employee's direct manager? Any manager in the department? How is the right one determined? What if they're on vacation?

---

## Define the State Machine

What statuses can the entity be in, and what transitions are valid?

Every action button on every form implies a state transition. Map them explicitly.

**Example — IT Ticket:**

```
NEW → IN_PROGRESS → WAITING_ON_CUSTOMER → RESOLVED → CLOSED
        ↓                                     ↓
    ESCALATED                              REOPENED → IN_PROGRESS
```

**Example — Purchase Order:**

```
DRAFT → SUBMITTED → APPROVED → ORDERED → RECEIVED → PAID
                  ↓
               REJECTED → (can be revised) → DRAFT
```

The states depend entirely on the domain. Don't assume a fixed set.

---

## Define Notifications

Who needs to know what, and when?

For every state transition, ask:

- Who cares that this just happened?
- What do they need to know?
- How should they be told? (email, in-app, SMS)
- Are there reminders for overdue items?

---

## Define Business Rules

Make implicit assumptions explicit.

Go through every field and every transition and ask:

- What would make this invalid?
- What are the edge cases?
- What are the time constraints?
- What are the ordering/dependency constraints?

**Examples:**

- *"Start date must be after today"* — seems obvious, but it must be stated
- *"Only the original submitter can cancel"* — a permission rule hidden in the flow
- *"Amounts over $10,000 require VP approval"* — a conditional routing rule

---

## Define Integration Points

What external systems does this process touch?

Only relevant if the process reads from or writes to other systems, APIs, or services.

---

## Define Success Criteria

How do we know this works?

Express as measurable outcomes, not vague goals.

---

## Define File Upload Handling

Only relevant if the process involves users uploading documents, images, or other files.

Ask yourself:

- What file types are accepted? Define a whitelist (e.g., PDF, PNG, JPEG — not "any file").
- What is the maximum file size?
- Single file or multiple files per upload?
- Where are files stored after upload? (temp path during process, or persisted permanently?)
- Can the user download or preview the uploaded file later?
- What happens if the upload fails mid-process?

---

## Define AI / Data Extraction

Only relevant if the process uses AI (Smart Workflow) to extract structured data from documents, text, or images.

Ask yourself:

- What is the input format? (uploaded PDF, image, free text, email body?)
- What fields must be extracted? Define each with name and type (String, Double, Date, List).
- Which fields are required vs. optional in the extracted output?
- What happens if confidence is low or a field cannot be found? (return null, flag for manual review, reject?)
- What happens if extraction fails completely? (notify user, allow manual entry, retry?)
- How is the extracted data validated after extraction? (format checks, business rules?)

---

## Expansion Heuristics

Use these patterns to expand vague user language into concrete detail:

| User Says | You Should Think About |
| --------- | ---------------------- |
| "some info" / "the details" / "the data" | What SPECIFIC fields? List every one. Each needs a name, type, and validation rule. |
| "extract" / "parse" / "AI" / "read from file" | Input format? Full extraction schema (all fields + types)? What if extraction fails or confidence is low? |
| "upload" / "attach" / "submit a file" | File types (whitelist)? Size limit? Single or multi? Storage location? Preview/download needed? |
| "save it" / "store it" | To what storage? What's the entity structure? What about auto-generated fields (id, timestamps, status)? |
| "fill in a form" / "enter details" | What sections? Which fields required vs optional? Conditional fields? Save draft? |
| "approve" / "review" | Who approves? What do they see? What actions can they take? Deadline? What about reject/return? |
| "the manager" / "the admin" | WHICH one? How is the right person determined? What if they're unavailable? |
| "notify" / "send alert" / "inform" | To whom? What channel? What content? On which events? Reminders for overdue? |
| "different types" / "categories" | Define the enum. List ALL values, not just the obvious ones. |
| "then it's done" | What are ALL the possible end states? Not just the happy path — what about rejection, cancellation, timeout, error? |
| "check if valid" | What specific rules? List each validation explicitly. |

---

## Common Pitfalls

- **Assuming field lists are complete** — Always ask "What else does [role] need to know?"
- **Forgetting the unhappy path** — Rejection, timeout, cancellation, errors
- **Ignoring cultural/regional variations** — Name structures, date formats, ID formats, currencies
- **Missing conditional fields** — "Required IF another field = X"
- **Forgetting system-generated fields** — id, createdDate, modifiedDate, status
- **Not defining enums explicitly** — A dropdown without listing the actual options is incomplete
- **Vague role assignment** — "Manager approves" → WHICH manager? How is the right one determined?
- **No state machine** — If the entity goes through stages, make the states explicit
- **Missing "back" flows** — Can tasks be sent back for revision? To whom?
- **No timeout handling** — What if nobody acts? Ever?

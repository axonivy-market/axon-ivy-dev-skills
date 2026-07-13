# Story Type: Custom Technical Story

Use this type when a technical need arises that does not fit any standard story type. Examples: migrating legacy data, configuring a third-party REST client, setting up a scheduled job, custom database queries.

**Do not overuse this type.** If the need can be covered by Security, Error & Expiry, or Roles & Config, use those instead.

---

## Required Sections

Every custom technical story must include all four sections below. A story missing any of these is incomplete.

### User Framing

> "This story enables [who] to [do what / benefit how]."

The beneficiary may be a developer, operations team, or end user. If you cannot write this sentence, the story is probably not worth implementing.

### Technical Motivation

Explain *why* this story exists:
- What breaks without it?
- Why does it not fit an existing story type?
- What layer or concern does it address?

### Implementation Details

Provide concrete, actionable steps. Do not write vague prose. Use tables, code snippets, and file paths.

At minimum include:
- Files to create or modify (with full paths)
- Configuration or code changes required
- Dependencies on other stories

### Acceptance Criteria

At least 3 verifiable criteria in checkbox format:

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

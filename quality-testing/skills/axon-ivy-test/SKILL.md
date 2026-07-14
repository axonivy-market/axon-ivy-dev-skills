---
name: axon-ivy-test
description: Entry point for creating and updating tests. Use this skill when user asks to write/update/delete tests.
---

## Step 0: Check Project Setup

**Check if `src_test/` folder exists and `pom.xml` has test dependency.**

Look for in `pom.xml`:

```xml
<dependency>
  <groupId>com.axonivy.ivy.api.test</groupId>
  <artifactId>ivy-test-api</artifactId>
  <scope>test</scope>
</dependency>
```

- **Not found** → Load `setup.md` to add testing infrastructure. Stop here.
- **Found** → Proceed to Step 1.

## Step 1: Investigate Project Conventions

**ALWAYS do this before writing any test.** Load `investigate.md` and follow its steps.

Scan existing tests to discover:

- Naming convention (`Test*.java` vs `*IT.java`)
- Package structure under `src_test/`
- Which annotations are in use (`@IvyTest`, `@IvyProcessTest`, `@RestResourceTest`)
- Existing test infrastructure (`RestResourceTest.java`, `ResourceResponder.java`, `LoggerAccess.java`)
- Existing helpers (`*TestClient.java`, `InMemory*.java`, `Dummy*.java`, `Mock*.java`)

Record findings for use in subsequent steps.

## Step 2: Detect Intent

Determine what the user wants to test by analyzing BOTH the user request AND the target code.

### Intent A: Pure Logic / Utility / Parser

Target has **no dependency on Ivy runtime**, REST, or external APIs.
Examples: data parsing, tree building, string formatting, event listeners with injected dependencies.

→ Load `unit.md` (Pure Unit Test section)

### Intent B: Service Using Ivy APIs

Target reads `Ivy.var()`, accesses CMS, or uses Ivy session — but does NOT call REST or execute processes.

→ Load `unit.md` (Ivy Unit Test section)

### Intent C: Workflow Process / BPM Flow

Target is a `.p.json` process OR user says "test this process".
Does NOT call external APIs.

→ Load `process.md`

### Intent D: Code Calling External REST API (Mocked)

Target calls external APIs (OpenAI, Azure, custom REST) but user wants fast, reliable, offline tests.

→ Load `rest.md` + `mock.md` + `resource.md` + `fixture.md`
→ Load `combos.md` for wiring guidance

### Intent E: End-to-End with Real API

User explicitly says "integration test", "e2e", "real API", or target is an `*IT.java` class.

→ Load `integration.md` + `fixture.md` + `log.md`

### Detection Guide

| Signal in target code | Intent |
| --- | --- |
| No `Ivy.*` imports, pure Java | A |
| `Ivy.var()`, `Ivy.cms()`, `Ivy.session()` | B |
| `.p.json` file or `BpmProcess` reference | C |
| `@Path`, `@GET`, `@POST`, REST client calls | D |
| User says "integration", "e2e", class ends with `IT` | E |

**When ambiguous, default to the simpler pattern** (A over B, D over E).

## Step 3: Load Support Patterns

After loading the primary pattern from Step 2, conditionally load these:

| Need | Load |
| --- | --- |
| Isolate with fake implementation (interface-based dep) | `test-doubles.md` |
| Build complex domain test objects | `test-doubles.md` (builder section) |
| Set Ivy variables for test | `fixture.md` |
| Mock external REST API | `mock.md` |
| Load JSON fixture data | `resource.md` |
| Assert log messages | `log.md` |
| Complex AssertJ chains | `assert.md` |
| Combining multiple patterns together | `combos.md` |

## Step 4: Apply Project Conventions

Use findings from Step 1 to ensure:

- Class naming matches project convention
- Package placement matches existing test structure
- **Reuse** existing test infrastructure — do NOT recreate helpers that already exist
- Follow same builder/helper patterns found in sibling tests

## Test File Naming & Location

| Type | Name | Location |
| --- | --- | --- |
| Unit / Process / REST test | `Test<ClassName>.java` | `src_test/<package>/Test<ClassName>.java` |
| Integration test | `<ClassName>IT.java` | `src_test/<package>/<ClassName>IT.java` |
| In-memory test double | `InMemory<Interface>.java` | `src_test/<package>/InMemory<Interface>.java` |
| Dummy provider | `Dummy<Interface>.java` | `src_test/<package>/dummy/Dummy<Interface>.java` |
| Mock handler | `<Name>Chat.java` | `src_test/<package>/mock/<Name>Chat.java` |

## Checklist

- [ ] Investigated existing test patterns in the project (Step 1)
- [ ] Identified correct test intent (Step 2)
- [ ] `src_test/` folder exists
- [ ] `pom.xml` has `ivy-test-api` dependency
- [ ] Test class has correct annotation for its type
- [ ] Reused existing test infrastructure where available
- [ ] Test naming follows project convention
- [ ] Loaded all necessary support pattern references

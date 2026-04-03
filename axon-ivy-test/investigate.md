# Investigate Project Test Conventions

Before writing any test, scan the project to match its existing conventions. Follow these steps:

## Step 1: Find the Test Root

Look for `src_test/` directories. The test project may be separate (e.g., `*-test/src_test/`).

## Step 2: Scan Test Infrastructure

Search for shared test utilities in `src_test/`:

- `ch/ivyteam/test/RestResourceTest.java` — composite annotation
- `ch/ivyteam/test/resource/ResourceResponder.java` — JSON fixture loader
- `ch/ivyteam/test/resource/ResourceResponse.java` — JUnit 5 parameter resolver
- `ch/ivyteam/test/log/LoggerAccess.java` — log capture extension

If these exist, **reuse them**. Do NOT recreate them.

## Step 3: Scan Test Helpers

Search `src_test/` for project-specific helpers:

- `*TestClient.java` — test API client wiring (e.g., `OpenAiTestClient`)
- `InMemory*.java` — in-memory test doubles
- `Dummy*.java` — dummy/stub implementations
- `Mock*.java` in `src_test/` — mock REST endpoint handlers
- `*Chat.java` in `mock/` packages — mock chat routing handlers

If helpers exist for the subsystem you're testing, **reuse them**.

## Step 4: Check Naming Patterns

Look at existing test class names:

- `Test<Name>.java` — unit/process/REST tests (prefix convention)
- `<Name>IT.java` — integration tests (suffix convention)
- Package mirroring: tests placed in same package as source class

## Step 5: Check for TestUtils

Look for `TestUtils.java` in `src/` or `src_test/`. If it exists with `getSystemProperty()`, use it for IT tests to read API keys.

## Step 6: Look at Sibling Tests

Find tests in the same package or feature area as the code under test. Match their:

- Annotation choice (`@IvyTest`, `@IvyProcessTest`, `@RestResourceTest`)
- Setup pattern (`@BeforeEach` structure and injected parameters)
- Assertion style (AssertJ fluent chains)
- Builder/helper method patterns (private static factory methods)

## Output

Record what you found. Use these findings to:

- Pick the correct annotation
- Reuse existing infrastructure (don't duplicate)
- Match naming and package conventions
- Follow the same setup/assertion style as sibling tests

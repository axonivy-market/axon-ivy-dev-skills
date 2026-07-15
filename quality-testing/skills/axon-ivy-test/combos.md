# Pattern Combinations

Guide for combining test patterns. Each row shows a real combination found in Axon Ivy projects.

## Combination Matrix

| Combo | Annotation | + Fixture | + Mock | + Resource | + Log | + TestDouble |
| --- | --- | --- | --- | --- | --- | --- |
| Pure unit | (none) | - | - | - | - | InMemory* |
| Ivy unit | `@IvyTest` | AppFixture | - | - | - | - |
| Static singleton | (none) | - | `MockedStatic<Xxx>` (see `singleton-mock.md`) | - | - | `*Fake` factories |
| Ivy unit + builders | `@IvyTest` | - | - | - | - | helper methods |
| Process test | `@IvyProcessTest` | - | - | - | - | - |
| REST full stack | `@RestResourceTest` | AppFixture | MockOpenAI | ResourceResponder | LoggerAccess | - |
| REST with handler | `@RestResourceTest` | AppFixture | *Chat class | ResourceResponder | - | - |
| IT with real API | `@IvyProcessTest` | AppFixture | - | - | LoggerAccess | - |

## Wiring: REST Mock Test (Full Pattern)

The most complex combination. Wire in this order in `@BeforeEach`:

**1. AppFixture** — Override the API base URL to point to local mock:

```java
fixture.var("AI.OpenAI.BaseUrl",
    OpenAiTestClient.localMockApiUrl("myTest"));
```

**2. MockOpenAI** — Define what the mock endpoint returns:

```java
MockOpenAI.defineChat(request -> responder.send("response.json"));
```

**3. ResourceResponder** — Serves JSON files from classpath next to the test class:

```
src_test/com/example/TestMyFeature/
  response.json
  response1.json
  response2.json
```

**4. LoggerAccess** (optional) — Capture HTTP transport logs:

```java
@RegisterExtension
LoggerAccess log = new LoggerAccess(LoggingHttpClient.class.getName());
```

### Complete Example

```java
@RestResourceTest
class TestMyFeature {

  private static final BpmProcess PROCESS = BpmProcess.name("MyProcess");

  @RegisterExtension
  LoggerAccess log = new LoggerAccess(LoggingHttpClient.class.getName());

  @BeforeEach
  void setup(AppFixture fixture, ResourceResponder responder) {
    fixture.var("AI.OpenAI.BaseUrl",
        OpenAiTestClient.localMockApiUrl("myTest"));
    MockOpenAI.defineChat(request -> responder.send("response.json"));
  }

  @Test
  void processesRequest(BpmClient client) {
    var res = client.start().process(PROCESS).execute();
    MyData data = res.data().last();
    assertThat(data.getResult()).contains("expected");
  }
}
```

## Decision: Mock vs. IT

| Factor | Mock (`@RestResourceTest`) | IT (`*IT.java`) |
| --- | --- | --- |
| Speed | Fast (ms) | Slow (seconds) |
| Reliability | Deterministic | Network-dependent |
| CI pipeline | Always runs | Separate profile `e2e.test` |
| API key needed | No | Yes |
| Tests real API contract | No | Yes |

**Default to mock tests.** Only create IT tests when:

- User explicitly asks for integration/e2e test
- Testing real API behavior that mocks cannot verify (e.g., structured output schema)

## Decision: Pure Unit vs. @IvyTest

| Factor | Pure Unit (no annotation) | `@IvyTest` |
| --- | --- | --- |
| Speed | Fastest | Fast |
| Ivy runtime | Not started | Started |
| Use when | Class has no `Ivy.*` dependency | Class uses `Ivy.var()`, CMS, session |
| Dependency injection | Constructor/method params | Ivy resolves automatically |

**Default to pure unit when possible.** Only use `@IvyTest` when the code under test directly calls `Ivy.*` APIs.

## Decision: When to Add Test Doubles

| Situation | Action |
| --- | --- |
| Service accepts interface via constructor | Create `InMemory*` implementation |
| Testing SPI loading/collection | Create `Dummy*` provider |
| Multiple tests need same complex object | Extract private static builder methods |
| Mock needs multi-turn routing logic | Extract to `*Chat.java` handler class |
| Simple one-off mock response | Inline lambda with `ResourceResponder` |

# Test Doubles & Data Builders

Patterns for isolating tests using in-memory implementations, dummy providers, and data builder methods.

## In-Memory Test Double

When a service depends on a storage/repository interface, create an in-memory implementation for test isolation.

### Pattern

```java
class InMemoryHistoryStorage implements HistoryStorage {

  private final List<AgentConversationEntry> entries = new ArrayList<>();

  @Override
  public List<AgentConversationEntry> findAll() {
    return entries;
  }

  @Override
  public List<AgentConversationEntry> findByCaseUuid(String caseUuid) {
    return entries.stream()
        .filter(e -> caseUuid.equalsIgnoreCase(e.getCaseUuid()))
        .toList();
  }

  @Override
  public void save(AgentConversationEntry entry) {
    if (!entries.contains(entry)) {
      entries.add(entry);
    }
  }

  @Override
  public void delete(AgentConversationEntry entry) {
    entries.remove(entry);
  }
}
```

### Usage in Test

```java
public class TestChatHistoryRepository {

  private InMemoryHistoryStorage storage;

  @BeforeEach
  void setUp() {
    storage = new InMemoryHistoryStorage();
    listener = new AgentResponseListener(
        new ChatHistoryRepository("case-1", "task-1", "agent", "elem", "proc", storage));
  }
}
```

### When to Use

- Service has constructor that accepts an interface
- Real implementation uses database, file system, or network
- You want fast, isolated, deterministic tests

### File Placement

Place in same package as the tests that use it:

```
src_test/<package>/InMemory<Interface>.java
```

Make the class **package-private** (no `public` modifier).

## Dummy Provider

For SPI/plugin systems, create dummy implementations to test the collection/loading mechanism.

### Pattern

```java
public class DummyChatModelProvider implements ChatModelProvider {

  public static final String NAME = "dummy";

  @Override
  public String name() {
    return NAME;
  }

  @Override
  public ChatModel createModel(ModelConfig config) {
    return new DummyChatModel();
  }
}
```

For guardrails or multi-provider testing, create multiple dummies:

```java
public class DummyInputGuardrail implements SmartWorkflowInputGuardrail { ... }
public class SecondDummyInputGuardrail implements SmartWorkflowInputGuardrail { ... }
```

### File Placement

```
src_test/<package>/dummy/Dummy<Interface>.java
```

## Test Data Builder Methods

For tests needing complex domain objects, use private static factory methods within the test class.

### Pattern

```java
@IvyTest
class TestAgentHistoryTreeBuilder {

  @Test
  void groupsByCase() {
    var entries = List.of(
        chatEntry("agent-1", LocalDateTime.of(2025, 3, 10, 14, 0)),
        chatEntry("agent-2", LocalDateTime.of(2025, 3, 10, 15, 0)));
    // ... assertions
  }

  // Simple builder
  private static AgentConversationEntry chatEntry(String agentId,
      LocalDateTime lastUpdated) {
    var e = new AgentConversationEntry();
    e.setAgentId(agentId);
    e.setCaseUuid("case-1");
    e.setTaskUuid("task-1");
    e.setLastUpdated(lastUpdated.toString());
    return e;
  }

  // Overloaded for variations
  private static AgentConversationEntry chatEntry(String agentId,
      LocalDateTime lastUpdated, List<ToolExecution> tools) {
    var e = chatEntry(agentId, lastUpdated);
    e.setToolExecutionsJson(JsonUtils.toJson(tools));
    return e;
  }

  private static ToolExecution toolExecution(String toolName) {
    return ToolExecution.builder()
        .request(ToolExecutionRequest.builder().name(toolName).build())
        .result("ok")
        .build();
  }
}
```

### Guidelines

- Keep builder methods `private static` within the test class
- Use method overloading to handle common vs. specific setups
- Name them after the domain concept (e.g., `chatEntry`), not the test
- Use `String.format` or text blocks for inline JSON fixtures

## Mock Chat Handler Class

For tests that need stateful or multi-turn mock API routing, extract the handler to its own class.

### Pattern

```java
public class SupportToolChat {

  private final ResourceResponder responder =
      new ResourceResponder(SupportToolChat.class);

  public Response toolTest(JsonNode request) {
    var messages = (ArrayNode) request.get("messages");
    if (hasToolCall(messages)) {
      return responder.send("response2.json");
    }
    return responder.send("response1.json");
  }
}
```

### Usage

```java
@BeforeEach
void setup(AppFixture fixture) {
  MockOpenAI.defineChat(new SupportToolChat()::toolTest);
}
```

### File Placement

```
src_test/<package>/mock/<HandlerName>Chat.java
```

Place JSON fixtures alongside the handler class, not the test class.

# Unit Testing

## Pure Unit Test (No Ivy Container)

When the class under test has **NO dependency on `Ivy.*` APIs**, use plain JUnit 5 without any Ivy annotation.

### File Location

`src_test/package/Test*.java`

### Pattern

```java
package package.test;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

public class TestMyParser {

  private final MyParser parser = new MyParser();

  @Test
  void parsesValidInput() {
    var result = parser.parse("{\"name\":\"test\"}");
    assertThat(result.getName()).isEqualTo("test");
  }

  @Test
  void handlesNull() {
    var result = parser.parse(null);
    assertThat(result).isNull();
  }
}
```

### With Constructor-Injected Dependencies

```java
public class TestChatHistoryRepository {

  private InMemoryHistoryStorage storage;
  private ChatHistoryRepository repository;

  @BeforeEach
  void setUp() {
    storage = new InMemoryHistoryStorage();
    repository = new ChatHistoryRepository("case-1", "task-1", "agent",
        "elem", "proc", storage);
  }

  @Test
  void savesEntry() {
    repository.save(buildEntry());
    assertThat(storage.findAll()).hasSize(1);
  }
}
```

No `@IvyTest` annotation. No Ivy container startup. **Fastest possible tests.**

Use this when the class accepts dependencies via constructor or method parameters.

## Ivy Unit Test (`@IvyTest`)

When the class under test **uses `Ivy.var()`, CMS, session, or other Ivy APIs**, use `@IvyTest` to start the Ivy container.

### File Location

`src_test/package/Test*.java`

### Basic Pattern

```java
package package.test;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

import ch.ivyteam.ivy.environment.IvyTest;

@IvyTest
public class TestMyService {

  @Test
  void testMethod() {
    var result = MyService.calculate(10);
    assertThat(result).isEqualTo(20);
  }
}
```

### With AppFixture

```java
@IvyTest
public class TestWithConfig {

  @BeforeEach
  void setup(AppFixture fixture) {
    fixture.var("myVar", "testValue");
  }

  @Test
  void testWithVariable() {
    assertThat(Ivy.var().get("myVar")).isEqualTo("testValue");
  }
}
```

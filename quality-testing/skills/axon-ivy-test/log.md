# Log Assertion

Log assertion utility with `LoggerAccess` extension.

## LoggerAccess Pattern

```java
import org.junit.jupiter.api.extension.RegisterExtension;
import ch.ivyteam.test.log.LoggerAccess;

public class TestWithLogging {

  @RegisterExtension
  LoggerAccess log = new LoggerAccess(MyService.class.getName());

  @Test
  void testLogsWarning() {
    MyService.doSomething();

    assertThat(log.warnings()).hasSize(1);
    assertThat(log.warnings()).contains("expected warning message");
  }

  @Test
  void testLogsInfo() {
    MyService.process();

    assertThat(log.infos())
        .anyMatch(msg -> msg.contains("Processing started"));
  }
}
```

## Available Methods

| Method | Returns |
|--------|---------|
| `errors()` | List of ERROR level messages |
| `warnings()` | List of WARN level messages |
| `infos()` | List of INFO level messages |
| `debugs()` | List of DEBUG level messages |
| `traces()` | List of TRACE level messages |
| `problems()` | Combined errors + warnings |

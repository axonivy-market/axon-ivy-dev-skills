# Integration Testing (IT)

End-to-end testing with real external APIs. Uses `*IT.java` naming and Maven `e2e.test` profile.

## When to Use

- Testing real API connectivity (OpenAI, Azure, Gemini, xAI)
- Validating structured output with real models
- Smoke-testing API key configuration
- User explicitly asks for "integration test", "e2e", or "real API" test

## File Naming

```
src_test/<package>/<FeatureName>IT.java
```

**NOT** `Test*.java` — the `IT` suffix is required for Maven Failsafe to pick it up.

## Maven Profile

IT tests run separately from unit tests:

```bash
mvn verify -Pe2e.test
```

This profile:

- Skips Surefire (unit tests)
- Runs Failsafe (integration tests matching `*IT.java`)

## API Key Handling

Use `TestUtils.getSystemProperty()` which reads from system property first, then environment variable:

```java
// TestUtils pattern (usually in src/ of test project)
public final class TestUtils {
  public static String getSystemProperty(String name) {
    return System.getProperty(name, System.getenv(name));
  }
}
```

Pass keys via `-DKEY_NAME=value` or set as environment variable `KEY_NAME`.

## Basic Pattern

```java
package com.example.model;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;

import ch.ivyteam.ivy.bpm.engine.client.element.BpmProcess;
import ch.ivyteam.ivy.bpm.exec.client.BpmClient;
import ch.ivyteam.ivy.bpm.exec.client.IvyProcessTest;
import ch.ivyteam.ivy.environment.Ivy;
import ch.ivyteam.ivy.application.app.AppFixture;
import ch.ivyteam.test.log.LoggerAccess;

@IvyProcessTest
class OpenAiModelIT {

  private static final BpmProcess PROCESS = BpmProcess.name("TestToolUser");

  @RegisterExtension
  LoggerAccess log = new LoggerAccess(LoggingHttpClient.class.getName());

  @BeforeEach
  void setup(AppFixture fixture) {
    fixture.var("AI.Models.DefaultProvider", "openai");
    fixture.var("AI.OpenAI.ApiKey",
        TestUtils.getSystemProperty("OPEN_AI_API_KEY"));
  }

  @Test
  void structuredOutput_e2e(BpmClient client) {
    Ivy.session().loginSessionUser("James", "secret");
    var res = client.start()
        .process(PROCESS.elementName("structuredOutput"))
        .as().session(Ivy.session())
        .execute();

    TestToolUserData data = res.data().last();
    assertThat(data.getPerson().getFirstName()).isEqualTo("James");
  }
}
```

## Key Differences from Mock Tests

| Factor | Mock (`@RestResourceTest`) | IT (`*IT.java`) |
| --- | --- | --- |
| Speed | Fast (ms) | Slow (seconds) |
| Reliability | Deterministic | Network-dependent |
| CI pipeline | Always runs (`mvn test`) | Separate profile (`mvn verify -Pe2e.test`) |
| API key needed | No | Yes (system property / env var) |
| Tests real API contract | No | Yes |
| Annotation | `@RestResourceTest` | `@IvyProcessTest` |

**Default to mock tests.** Only create IT tests when explicitly asked or when testing real API behavior that mocks cannot verify.

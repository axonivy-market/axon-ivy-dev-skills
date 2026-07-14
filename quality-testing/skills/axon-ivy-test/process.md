# Process Testing

Workflow process testing with `@IvyProcessTest` and `BpmClient`.

## File Location

`src_test/package/Test*.java`

## Basic Pattern

```java
package package.test;

import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.Test;
import ch.ivyteam.ivy.bpm.exec.client.IvyProcessTest;
import ch.ivyteam.ivy.bpm.exec.client.BpmClient;
import ch.ivyteam.ivy.bpm.engine.client.element.BpmProcess;

@IvyProcessTest
public class TestMyProcess {

  private static final BpmProcess MY_PROCESS = BpmProcess.name("MyProcess");

  @Test
  void testProcessElement(BpmClient client) {
    var result = client.start()
        .process(MY_PROCESS.elementName("myElement"))
        .execute();

    MyData data = result.data().last();
    assertThat(data.getStatus()).isEqualTo("COMPLETED");
  }
}
```

## With Session Login

```java
@Test
void testWithUser(BpmClient client) {
  Ivy.session().loginSessionUser("testUser", "password");
  var result = client.start()
      .process(MY_PROCESS)
      .as().session(Ivy.session())
      .execute();
}
```

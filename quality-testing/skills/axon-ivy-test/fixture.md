# AppFixture

Test configuration with `AppFixture` for variables and environment setup.

## Injection Pattern

```java
import ch.ivyteam.ivy.application.app.AppFixture;

@IvyTest
public class TestWithFixture {

  @BeforeEach
  void setup(AppFixture fixture) {
    // Set Ivy variables
    fixture.var("myNamespace.apiKey", "test-key");
    fixture.var("myNamespace.baseUrl", "http://localhost/mock");

    // Variables are reset after each test
  }

  @Test
  void testUsingVariables() {
    String apiKey = Ivy.var().get("myNamespace.apiKey");
    assertThat(apiKey).isEqualTo("test-key");
  }
}
```

## Combined with ResourceResponder

```java
@RestResourceTest
public class TestCombined {

  @BeforeEach
  void setup(AppFixture fixture, ResourceResponder responder) {
    fixture.var("api.url", "http://mock/api");
    MockApi.define(req -> responder.send("response.json"));
  }
}
```

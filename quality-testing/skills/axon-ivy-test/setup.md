# Test Setup

Add testing infrastructure to an existing Axon Ivy project.

## Folder Structure to Add

```text
existing-project/
├── pom.xml              # UPDATE: add test dependency
└── src_test/            # CREATE: test source folder
    └── package/
        └── Test*.java
```

## pom.xml - Add Test Dependency

```xml
<dependencies>
  <!-- Existing dependencies... -->

  <!-- ADD this for testing -->
  <dependency>
    <groupId>com.axonivy.ivy.api.test</groupId>
    <artifactId>ivy-test-api</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>

<build>
  <!-- ADD this to specify test source -->
  <testSourceDirectory>src_test</testSourceDirectory>

  <plugins>
    <!-- Existing plugins... -->
  </plugins>
</build>
```

## Create First Test

**File:** `src_test/package/TestMyService.java`

```java
package package;

import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.Test;
import ch.ivyteam.ivy.environment.IvyTest;

@IvyTest
public class TestMyService {

  @Test
  void testExample() {
    assertThat(true).isTrue();
  }
}
```

## Run Tests

```bash
mvn test
```

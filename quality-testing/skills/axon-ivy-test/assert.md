# AssertJ Assertions

AssertJ assertion patterns for Axon Ivy testing.

## Import

```java
import static org.assertj.core.api.Assertions.assertThat;
```

## Common Patterns

```java
// String assertions
assertThat(result).isEqualTo("expected");
assertThat(result).contains("partial");
assertThat(result).isEqualToIgnoringCase("EXPECTED");

// Collection assertions
assertThat(list).hasSize(3);
assertThat(list).contains("item1", "item2");
assertThat(list).containsOnly("a", "b", "c");
assertThat(list).isEmpty();

// Type assertions
assertThat(object).isInstanceOf(MyClass.class);
assertThat(object).isNotNull();

// Extracting nested values
assertThat(list)
    .extracting(Item::getName)
    .containsOnly("name1", "name2");

// Map assertions
assertThat(map.entrySet())
    .extracting(Entry::getKey)
    .containsOnly("key1", "key2");

// Boolean assertions
assertThat(condition).isTrue();
assertThat(condition).isFalse();

// Exception assertions
assertThatThrownBy(() -> service.call())
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("invalid");
```

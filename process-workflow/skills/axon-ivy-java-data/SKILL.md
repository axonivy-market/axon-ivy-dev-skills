---
name: axon-ivy-java-data
description: Rules and patterns for Java model classes, enums, DTOs in Axon Ivy projects. Do not apply for .d.json files.
---

## Use Together With

- `axon-ivy-repository` - For persistence with Ivy.repo()

## File Locations

| Type | Location |
|------|----------|
| Model Class | `src/package/model/` |
| Enum | `src/package/model/` |
| DTO | `src/package/dto/` |

## Naming Conventions

- **Classes**: PascalCase (e.g., `Employee`, `LeaveRequest`, `ProjectStatus`)
- **Fields**: camelCase (e.g., `employeeName`, `startDate`)
- **Enums**: PascalCase class, UPPER_SNAKE_CASE values (e.g., `EntityStatus.IN_PROGRESS`)
- **Packages**: all lowercase, dot-separated (e.g., `hr.onboarding.model`)

## Complete Entity Example

**File:** `src/package/model/Entity.java`

```java
package package.model;

import java.io.Serializable;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

// Rule: All model classes used in process data MUST implement Serializable
public class Entity implements Serializable {

  private static final long serialVersionUID = 1L;

  private String id;
  private String name;
  private EntityStatus status;
  private List<String> tags;
  // Rule: Use java.time.LocalDate/LocalDateTime for date fields — never use java.util.Date
  private LocalDate createdDate;

  public Entity() {
    // Rule: Always initialize id using UUID.randomUUID().toString()
    this.id = UUID.randomUUID().toString();
    
    // Rule: Always initialize status enums to a sensible default
    this.status = EntityStatus.NEW;
    
    // Rule: Initialize List fields to new ArrayList<>() to avoid null checks
    this.tags = new ArrayList<>();

    this.createdDate = LocalDate.now();
  }

  // Getters and Setters
  public String getId() { return id; }
  public void setId(String id) { this.id = id; }

  ...
}
```

**Accompanying Enum:** `src/package/model/EntityStatus.java`

```java
package package.model;

public enum EntityStatus {
  NEW("New"),
  IN_PROGRESS("In Progress"),
  COMPLETED("Completed"),
  CANCELLED("Cancelled");

  private final String description;

  EntityStatus(String description) {
    this.description = description;
  }

  public String getDescription() {
    return description;
  }
}
```

## Optional Extension: AI Description Integration

**Only use if the project depends on `smart-workflow` (check `pom.xml`).

Add `@Description` annotations for AI/LLM processing:

```java
package package.model;

import dev.langchain4j.model.output.structured.Description;
import java.io.Serializable;
import java.util.List;

@Description("Business entity with lifecycle status and categorization")
public class Entity implements Serializable {

  private static final long serialVersionUID = 1L;

  @Description("Human-readable name")
  private String name;

  @Description("Current lifecycle status: NEW, IN_PROGRESS, COMPLETED, or CANCELLED")
  private EntityStatus status;

}
```

## JPA/SQL Persistence (Advanced Approach)

**Use this approach ONLY when the user explicitly requests SQL/JPA persistence.**
For the default/simple approach, use `axon-ivy-repository` (Ivy.repo()) instead.

This approach uses `persistence-utils` library with JPA/Hibernate for SQL database access.
It requires: `databases.yaml`, `persistence.xml`, JPA entities, DAOs, and service wrappers.

---

## Required Dependencies (pom.xml)

```xml
<dependency>
    <groupId>com.axonivy.utils.persistence</groupId>
    <artifactId>persistence-utils</artifactId>
    <version>12.0.2</version>
    <type>jar</type>
</dependency>
<dependency>
    <groupId>org.hibernate</groupId>
    <artifactId>hibernate-jpamodelgen</artifactId>
    <version>5.4.12.Final</version>
</dependency>
```

---

## 1. Database Configuration

### databases.yaml

Location: `<project>/config/databases.yaml`

```yaml
# yaml-language-server: $schema=https://json-schema.axonivy.com/14.0-dev/config/databases.json
Databases:
  MyDatabase:
    Url: jdbc:sqlserver://localhost;databaseName=MY_DB
    Driver: com.microsoft.sqlserver.jdbc.SQLServerDriver
    UserName: sa
    Password: ${decrypt:ENCRYPTED_VALUE_HERE}
    Properties:
      encrypt: 'false'
```

Common JDBC drivers:

| Database | Driver Class | URL Format |
|----------|-------------|------------|
| SQL Server | `com.microsoft.sqlserver.jdbc.SQLServerDriver` | `jdbc:sqlserver://host;databaseName=DB` |
| PostgreSQL | `org.postgresql.Driver` | `jdbc:postgresql://host:5432/DB` |
| MySQL | `com.mysql.cj.jdbc.Driver` | `jdbc:mysql://host:3306/DB` |

### persistence.xml

Location: `<project>/config/persistence.xml`

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<persistence xmlns="http://xmlns.jcp.org/xml/ns/persistence"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             version="2.2"
             xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/persistence
                                 http://xmlns.jcp.org/xml/ns/persistence/persistence_2_2.xsd">

    <persistence-unit name="MyDatabase">
        <non-jta-data-source>MyDatabase</non-jta-data-source>
        <class>com.example.entity.Customer</class>
        <class>com.example.entity.Order</class>
        <exclude-unlisted-classes>true</exclude-unlisted-classes>
        <properties>
            <property name="hibernate.id.new_generator_mappings" value="false"/>
        </properties>
    </persistence-unit>
</persistence>
```

**Critical**: `<non-jta-data-source>` value MUST match the database name in `databases.yaml`. Every entity class MUST be listed.

---

## 2. JPA Entity Pattern

Entities extend `AuditableIdEntity` from `persistence-utils`, which provides:
`id`, `version`, audit fields (`createdByUserName`, `createdDate`, `modifiedByUserName`, `modifiedDate`), and soft-delete fields.

**File:** `src/package/sql/entity/MyEntity.java`

```java
package com.example.project.sql.entity;

import java.util.Date;
import java.util.List;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.EnumType;
import javax.persistence.Enumerated;
import javax.persistence.FetchType;
import javax.persistence.ForeignKey;
import javax.persistence.JoinColumn;
import javax.persistence.JoinTable;
import javax.persistence.ManyToMany;
import javax.persistence.OneToMany;
import javax.persistence.OneToOne;
import javax.persistence.Table;
import javax.validation.constraints.NotNull;

import com.axonivy.utils.persistence.beans.AuditableIdEntity;

import com.example.project.sql.common.TableAndColumnDictionary;

@Entity
@Table(name = TableAndColumnDictionary.TABLE_MY_ENTITY)
public class MyEntity extends AuditableIdEntity {

    private static final long serialVersionUID = 1L;

    @Column(name = TableAndColumnDictionary.COLUMN_TITLE, length = 500)
    @NotNull
    private String title;

    @Enumerated(EnumType.STRING)
    @Column(name = TableAndColumnDictionary.COLUMN_STATUS, length = 50)
    private Status status;

    @Column(name = TableAndColumnDictionary.COLUMN_TARGET_DATE)
    private Date targetDate;

    @OneToOne
    @JoinColumn(name = TableAndColumnDictionary.COLUMN_ORG_UNIT_FK,
            foreignKey = @ForeignKey(name = TableAndColumnDictionary.FK_ENTITY_ORG_UNIT),
            referencedColumnName = TableAndColumnDictionary.COLUMN_ID)
    private OrganizationUnit orgUnit;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = TableAndColumnDictionary.COLUMN_ENTITY_FK)
    private List<Note> notes;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(name = TableAndColumnDictionary.TABLE_ENTITY_DOCUMENT,
            joinColumns = @JoinColumn(name = TableAndColumnDictionary.COLUMN_ENTITY_FK),
            inverseJoinColumns = @JoinColumn(name = TableAndColumnDictionary.COLUMN_DOCUMENT_FK))
    private List<Document> documents;

    // Getters and setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public Status getStatus() { return status; }
    public void setStatus(Status status) { this.status = status; }
    // ... remaining getters/setters
}
```

### TableAndColumnDictionary

**ALWAYS** create a constants class for table/column names:

```java
public class TableAndColumnDictionary {
    public static final String TABLE_MY_ENTITY = "MyEntity";
    public static final String TABLE_ENTITY_DOCUMENT = "Entity_Document";
    public static final String COLUMN_ID = "id";
    public static final String COLUMN_TITLE = "title";
    public static final String COLUMN_STATUS = "status";
    public static final String COLUMN_TARGET_DATE = "targetDate";
    public static final String COLUMN_ENTITY_FK = "entityId";
    public static final String COLUMN_DOCUMENT_FK = "documentId";
    public static final String COLUMN_ORG_UNIT_FK = "orgUnitId";
    public static final String FK_ENTITY_ORG_UNIT = "FK_Entity_OrgUnit";

    private TableAndColumnDictionary() {}
}
```

---

## 3. DAO Pattern

DAOs extend `AuditableIdDAO<Entity_, Entity>` from `persistence-utils`.

**File:** `src/package/sql/dao/MyEntityDAO.java`

```java
package com.example.project.sql.dao;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.collections4.CollectionUtils;

import com.axonivy.utils.persistence.dao.AuditableIdDAO;
import com.axonivy.utils.persistence.dao.CriteriaQueryContext;

import com.example.project.sql.entity.MyEntity;
import com.example.project.sql.entity.MyEntity_;
import ch.ivyteam.ivy.environment.Ivy;

public class MyEntityDAO extends AuditableIdDAO<MyEntity_, MyEntity> implements ProjectBaseDAO {

    @Override
    protected Class<MyEntity> getType() {
        return MyEntity.class;
    }

    public MyEntity findByTitle(String title) {
        try (CriteriaQueryContext<MyEntity> query = initializeQuery()) {
            query.whereEq(MyEntity_.title, title);
            List<MyEntity> results = findByCriteria(query);
            return CollectionUtils.isNotEmpty(results) ? results.get(0) : null;
        } catch (Exception e) {
            Ivy.log().error("Failed to find MyEntity by title {0}", e, title);
            return null;
        }
    }
}
```

**Inherited methods** (do NOT re-implement): `save()`, `saveAll()`, `findAll()`, `findById()`, `delete()`, `deleteAll()`

### CriteriaQueryContext API

| Method | Purpose |
|--------|---------|
| `query.whereEq(field, value)` | WHERE field = value |
| `query.where(predicate)` | Add custom JPA Predicate |
| `query.r.get(Entity_.field)` | Get field path for predicates |
| `query.c.greaterThan(path, value)` | Build > predicate |
| `query.c.like(path, pattern)` | Build LIKE predicate |
| `findByCriteria(query)` | Execute and return results |

---

## 4. Service Layer Pattern

Static wrapper classes over DAO instances.

**File:** `src/package/sql/service/MyEntityService.java`

```java
package com.example.project.sql.service;

import java.util.List;
import javax.persistence.PersistenceException;

import com.example.project.sql.dao.MyEntityDAO;
import com.example.project.sql.entity.MyEntity;
import ch.ivyteam.ivy.environment.Ivy;

public class MyEntityService {

    private static MyEntityDAO myEntityDAO = new MyEntityDAO();

    private MyEntityService() {}

    public static MyEntity save(MyEntity entity) {
        return myEntityDAO.save(entity);
    }

    public static List<MyEntity> findAll() {
        return myEntityDAO.findAll();
    }

    public static MyEntity findById(String id) {
        return myEntityDAO.findById(id);
    }

    public static void delete(MyEntity entity) {
        try {
            myEntityDAO.delete(entity);
        } catch (PersistenceException e) {
            Ivy.log().error("Cannot delete MyEntity with id = " + entity.getId(), e);
        }
    }

    public static MyEntity findByTitle(String title) {
        return myEntityDAO.findByTitle(title);
    }
}
```

---

## Critical Rules

- **Passwords MUST use `${decrypt:...}`** — never store plain text in databases.yaml
- **Every entity MUST be registered** in `persistence.xml` under the correct persistence unit
- **ALWAYS use `TableAndColumnDictionary`** for table/column names — no string literals in annotations
- **Use `EnumType.STRING`** (not ORDINAL) for enum columns
- **Use `FetchType.LAZY`** for collections
- **Always wrap queries** in `try (CriteriaQueryContext<T> query = initializeQuery())`
- **Use metamodel classes (`Entity_`)** for type-safe field references
- **Catch exceptions and log** with `Ivy.log().error()` — never let exceptions propagate unhandled
- **Private constructor** on service classes — all methods are static

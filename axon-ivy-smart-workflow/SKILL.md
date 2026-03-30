---
name: axon-ivy-smart-workflow
description: Create AI-powered data extraction and processing in Axon Ivy workflows using the Smart Workflow AgenticProcessCall element.
---

# Axon Ivy Smart Workflow - AI Extraction Skill

Use this skill when creating AI-powered data extraction or processing in Axon Ivy workflows.

## Prerequisites Check

### Step 1: Check pom.xml for Smart Workflow Dependency

Before creating Smart Workflow elements, verify the project's `pom.xml` contains the required dependencies:

```xml
<dependency>
  <groupId>com.axonivy.utils.ai</groupId>
  <artifactId>smart-workflow</artifactId>
  <version>13.2.0-SNAPSHOT</version>
  <type>iar</type>
</dependency>
<dependency>
  <groupId>com.axonivy.utils.ai</groupId>
  <artifactId>smart-workflow-openai</artifactId>
  <version>13.2.0-SNAPSHOT</version>
  <type>iar</type>
</dependency>
```

### Step 2: If Dependencies Missing

1. **Search for smart-workflow project in workspace:**
   - Look for `smart-workflow/pom.xml` or `smart-workflow-openai/pom.xml` in the workspace
   - Use glob pattern: `**/smart-workflow/pom.xml`

2. **If smart-workflow project EXISTS in workspace:**
   - Add the dependencies to the target project's `pom.xml`
   - Use the version from the smart-workflow project's pom.xml

3. **If smart-workflow project DOES NOT EXIST in workspace** (no `pom.xml` found AND no `smart-workflow-*.iar` file found):
   - **Use the `ivy-market-import` skill** to import the smart-workflow library into the codebase before doing anything else.
   - After import completes, continue with the rest of this skill.

## Creating Smart Workflow Elements

### ProgramInterface Element for AI Extraction

Use `ProgramInterface` with `AgenticProcessCall` to call AI for structured data extraction.

```json
{
  "id" : "f1",
  "type" : "ProgramInterface",
  "name" : "Extract Data with AI",
  "config" : {
    "javaClass" : "com.axonivy.utils.smart.workflow.AgenticProcessCall",
    "userConfig" : {
      "system" : "You are an AI assistant. Extract the requested information from the provided text.",
      "tools" : "[]",
      "resultType" : "package.model.OutputClass.class",
      "resultMapping" : "in.outputVariable",
      "query" : "Extract information from this text:\n\n<TEXT>\n<%= in.inputText %>\n</TEXT>"
    }
  },
  "visual" : {
    "at" : { "x" : 256, "y" : 64 },
    "size" : { "width" : 128 }
  },
  "boundaries" : [ {
      "id" : "f2",
      "type" : "ErrorBoundaryEvent",
      "config" : {
        "errorCode" : "ivy:error:program:exception",
        "output" : {
          "map" : {
            "out" : "in",
            "out.error" : "error"
          }
        }
      },
      "visual" : {
        "at" : { "x" : 288, "y" : 104 }
      },
      "connect" : [
        { "id" : "f10", "to" : "errorHandler" }
      ]
    } ],
  "connect" : [
    { "id" : "f11", "to" : "nextElement" }
  ]
}
```

## userConfig Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `system` | Yes | System prompt instructing the AI what to extract |
| `query` | Yes | User query with input data (use `<%= in.variable %>` for template expansion) |
| `resultType` | Yes | **MUST end with `.class`** - The Java class for structured output |
| `resultMapping` | Yes | Variable to store the result (e.g., `in.result`) |
| `tools` | No | List of callable sub-processes as tools (default: `"[]"`) |
| `model` | No | AI model to use (e.g., `"gpt-4.1"`) |

## IMPORTANT NOTES

### 1. resultType MUST End with `.class`

**CORRECT:**
```json
"resultType" : "hr.onboarding.model.EmployeeInfo.class"
```

**WRONG:**
```json
"resultType" : "hr.onboarding.model.EmployeeInfo"
```

### 2. Output Type MUST Be a Single Object (NOT a List)

The AI extraction **cannot return a List directly**. Always use a wrapper object.

**WRONG - Will not work:**
```json
"resultType" : "java.util.List.class"
"resultType" : "List<hr.model.Item>.class"
```

**CORRECT - Use a wrapper class:**
```java
// Create a wrapper class
public class ExtractionResult {
  private List<Item> items;
  // getters and setters
}
```
```json
"resultType" : "hr.model.ExtractionResult.class"
```

### 3. Use @Description Annotations for Better Extraction

When creating model classes for AI extraction, use LangChain4j `@Description` annotations:

```java
package hr.onboarding.model;

import dev.langchain4j.model.output.structured.Description;

@Description("Employee identification information")
public class EmployeeInfo {

  @Description("System username for the employee")
  private String employeeUsername;

  @Description("Employee's first/given name")
  private String employeeFirstName;

  @Description("Employee's last/family name")
  private String employeeLastName;

  // getters and setters
}
```

## Complete Example: Employee Data Extraction Subprocess

### Data Class: ExtractEmployeeData.d.json

```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/data-class.json",
  "simpleName" : "ExtractEmployeeData",
  "namespace" : "hr.onboarding.agent",
  "fields" : [ {
    "name" : "inputText",
    "type" : "String",
    "comment" : "Raw input text"
  }, {
    "name" : "employeeInfo",
    "type" : "hr.onboarding.model.EmployeeInfo",
    "comment" : "Extracted employee information"
  }, {
    "name" : "error",
    "type" : "ch.ivyteam.ivy.bpm.error.BpmError"
  }, {
    "name" : "errorStr",
    "type" : "String"
  } ]
}
```

### Process: ExtractEmployeeData.p.json

```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/process.json",
  "id" : "19CF01A0E1B2C3D4",
  "kind" : "CALLABLE_SUB",
  "config" : {
    "data" : "hr.onboarding.agent.ExtractEmployeeData"
  },
  "elements" : [ {
      "id" : "f0",
      "type" : "CallSubStart",
      "name" : "extractEmployeeData(String)",
      "config" : {
        "signature" : "extractEmployeeData",
        "input" : {
          "params" : [
            { "name" : "inputText", "type" : "String", "desc" : "Raw text containing employee information" }
          ],
          "map" : {
            "out.inputText" : "param.inputText",
            "out.employeeInfo" : "new hr.onboarding.model.EmployeeInfo()"
          }
        },
        "result" : {
          "params" : [
            { "name" : "employeeInfo", "type" : "hr.onboarding.model.EmployeeInfo", "desc" : "Extracted employee information" },
            { "name" : "error", "type" : "String", "desc" : "Error message if extraction fails" }
          ],
          "map" : {
            "result.employeeInfo" : "in.employeeInfo",
            "result.error" : "in.errorStr"
          }
        }
      },
      "visual" : { "at" : { "x" : 96, "y" : 64 } },
      "connect" : [ { "id" : "f6", "to" : "f1" } ]
    }, {
      "id" : "f1",
      "type" : "ProgramInterface",
      "name" : "Extract Employee Data",
      "config" : {
        "javaClass" : "com.axonivy.utils.smart.workflow.AgenticProcessCall",
        "userConfig" : {
          "system" : "You are an HR data extraction assistant. Extract employee identification information from the provided text.\n\nEXTRACT THE FOLLOWING FIELDS:\n1. employeeUsername: System username\n2. employeeFirstName: First name\n3. employeeLastName: Last name\n4. employeeId: Employee ID number\n\nRULES:\n- Names should be properly capitalized\n- If username not provided, generate as firstname.lastname (lowercase)\n- Return an EmployeeInfo object with the extracted data.",
          "tools" : "[]",
          "resultType" : "hr.onboarding.model.EmployeeInfo.class",
          "resultMapping" : "in.employeeInfo",
          "query" : "Extract employee information from this text:\n\n<TEXT>\n<%= in.inputText %>\n</TEXT>"
        }
      },
      "visual" : { "at" : { "x" : 256, "y" : 64 }, "size" : { "width" : 128 } },
      "boundaries" : [ {
          "id" : "f2",
          "type" : "ErrorBoundaryEvent",
          "config" : {
            "errorCode" : "ivy:error:program:exception",
            "output" : { "map" : { "out" : "in", "out.error" : "error" } }
          },
          "visual" : { "at" : { "x" : 288, "y" : 104 } },
          "connect" : [ { "id" : "f7", "to" : "f4", "via" : [ { "x" : 288, "y" : 160 } ] } ]
        } ],
      "connect" : [ { "id" : "f8", "to" : "f3" } ]
    }, {
      "id" : "f3",
      "type" : "CallSubEnd",
      "visual" : { "at" : { "x" : 448, "y" : 64 } }
    }, {
      "id" : "f4",
      "type" : "Script",
      "name" : "Parse Error",
      "config" : {
        "output" : {
          "code" : "in.errorStr = in.error != null ? in.error.getMessage() : \"Unknown error\";"
        }
      },
      "visual" : { "at" : { "x" : 384, "y" : 160 } },
      "connect" : [ { "id" : "f9", "to" : "f3", "via" : [ { "x" : 448, "y" : 160 } ] } ]
    } ]
}
```

## Using Tools (Callable Sub-Processes)

To give the AI access to tools (sub-processes it can call):

```json
"userConfig" : {
  "system" : "You are an assistant with access to tools...",
  "tools" : "[\"searchDatabase\", \"createRecord\", \"sendNotification\"]",
  "resultType" : "hr.model.AgentResponse.class",
  "resultMapping" : "in.response",
  "query" : "<%= in.userRequest %>"
}
```

Each tool name must correspond to a callable sub-process signature in the project.

## System Prompt Best Practices

1. **Be specific** about what to extract
2. **List all fields** the AI should populate
3. **Provide rules** for handling edge cases
4. **Specify formats** for dates, numbers, etc.
5. **Use examples** if the extraction is complex

```json
"system" : "You are a data extraction assistant.\n\nEXTRACT:\n1. fieldName: Description of what to extract\n2. anotherField: Another description\n\nRULES:\n- Rule 1\n- Rule 2\n\nFORMATS:\n- Dates: yyyy-MM-dd\n- Phone: +1-XXX-XXX-XXXX"
```

## Query Template Patterns

### Simple Text Input
```json
"query" : "Process this text:\n\n<%= in.inputText %>"
```

### JSON Object Input
```json
"query" : "Process this data:\n\n<%= dev.langchain4j.internal.Json.toJson(in.dataObject) %>"
```

### Multiple Inputs
```json
"query" : "Context: <%= in.context %>\n\nData to process:\n<%= in.inputData %>\n\nInstructions: <%= in.instructions %>"
```

### Binary File Input (Image or PDF)
Pass binary files directly in the query — AgenticProcessCall understands `InputStream` and `Binary` objects natively. No base64 encoding needed.

```json
"query" : "Extract all data from this invoice:\n<%= in.uploadedFile %>"
```

Supported data types for file variables:

| Type | How to obtain | Notes |
|------|--------------|-------|
| `java.io.InputStream` | From uploaded file or CMS | Preferred for images |
| `ch.ivyteam.ivy.scripting.objects.Binary` | From CMS binary resource | Preferred for PDFs |
| `java.io.File` | From file system path | Works for both |
| CMS binary directly | `ivy.cms.co("/path/to/resource")` | Embedded in template |

**Example: Extract invoice from user-uploaded file**

Data class:
```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/data-class.json",
  "simpleName" : "ExtractInvoiceData",
  "namespace" : "invoice.extraction",
  "fields" : [ {
    "name" : "uploadedFile",
    "type" : "java.io.InputStream",
    "comment" : "Uploaded invoice file (PDF or image)"
  }, {
    "name" : "invoice",
    "type" : "invoice.model.Invoice",
    "comment" : "Extracted invoice data"
  }, {
    "name" : "error",
    "type" : "ch.ivyteam.ivy.bpm.error.BpmError"
  }, {
    "name" : "errorStr",
    "type" : "String"
  } ]
}
```

AgenticProcessCall query:
```json
"query" : "Extract all invoice data from this document:\n<%= in.uploadedFile %>"
```

**Type guidance for financial/document extraction:**

| Field type | Use | Reason |
|-----------|-----|--------|
| `java.lang.Double` | Prices, amounts, totals | Sufficient for display and calculation |
| `java.lang.Integer` | Quantities | Whole numbers only |
| `String` | Dates, invoice number, IBAN | Return as string, parse in Script if needed |
| `List<T>` (via wrapper) | Line items | Must be wrapped — see Note 2 above |

**System prompt example for invoice extraction:**
```json
"system" : "You are an invoice data extraction assistant.\n\nEXTRACT THE FOLLOWING:\n1. invoiceNumber: The invoice identifier\n2. invoiceDate: Issue date (format: yyyy-MM-dd)\n3. dueDate: Payment due date (format: yyyy-MM-dd)\n4. vendorName: Name of the issuing company\n5. customerName: Name of the billed customer\n6. items: List of line items (description, quantity, unitPrice, total)\n7. subtotal: Amount before tax\n8. vatRate: VAT percentage (e.g. 8.1)\n9. vatAmount: Tax amount\n10. totalDue: Final amount due\n\nRULES:\n- All amounts are numbers (no currency symbols)\n- Return null for fields not found in the document"
```

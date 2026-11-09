# Example: Employee Data Extraction Sub-process

A callable sub-process that takes raw text, lets the AI extract an `EmployeeInfo` object, and returns it. On failure it returns `null` plus an error message, so the caller decides what to do.

## Result class: EmployeeInfo.java

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

  @Description("Employee ID number, null if not in the text")
  private String employeeId;

  // getters and setters
}
```

## Data class: ExtractEmployeeData.d.json

```json
{
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

## Process: ExtractEmployeeData.p.json

```json
{
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
          "system" : "You are an HR data extraction assistant. Extract employee identification information from the provided text.\n\nEXTRACT THE FOLLOWING FIELDS:\n1. employeeUsername: System username\n2. employeeFirstName: First name\n3. employeeLastName: Last name\n4. employeeId: Employee ID number\n\nRULES:\n- Names should be properly capitalized\n- If username not provided, generate as firstname.lastname (lowercase)\n- Return null for employeeId if it is not in the text, never guess it",
          "query" : "Extract employee information from this text:\n\n<TEXT>\n<%=in.inputText%>\n</TEXT>",
          "tools" : "",
          "resultType" : "hr.onboarding.model.EmployeeInfo.class",
          "resultMapping" : "in.employeeInfo"
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

## Variations

- **File instead of text:** make `inputText` a `java.io.InputStream` or `Binary` field and use `"query" : "Extract employee information from this document:\n<%=in.document%>"`. Set the field to `null` in a Script after the agent.
- **Guardrails or circuit breaker:** add another boundary per `smartworkflow:...` code (see "Error codes to catch" in [SKILL.md](../SKILL.md)) and route it to the same "Parse Error" script. Use separate scripts only when the handling differs.

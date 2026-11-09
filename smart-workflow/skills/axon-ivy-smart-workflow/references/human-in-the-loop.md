# Human-in-the-Loop

With this pattern, an agent can pause, ask a human to decide, and then continue the **same** conversation with the answer.

## How it works

1. The agent calls a tool sub-process (e.g. `askUserDecision`), and that tool throws a BpmError.
2. Smart Workflow saves the conversation and writes its id into the process data field **`aiMemoryId`**. The field name is fixed by convention.
3. An `ErrorBoundaryEvent` on the agent element catches the error and routes to a `UserTask`.
4. When the user has answered, `new DecisionMaker(in.aiMemoryId).resolve(answer)` stores the answer as the tool's result.
5. The flow loops back to the **same** agent element. It restores the conversation from `aiMemoryId`, sees the tool result and finishes. After a successful run, `aiMemoryId` is cleared.

## Requirements

- The process data class has a field `aiMemoryId` of type `String`.
- The tool `CallSubStart` is tagged `tool` and is listed in the agent's `tools`.
- The decision types are your own data classes. Smart Workflow does not ship them.

## Data classes

`HumanDecision.d.json`:

```json
{
  "simpleName" : "HumanDecision",
  "namespace" : "com.example.human",
  "fields" : [ {
    "name" : "question",
    "comment" : "required: A descriptive text to let a human decide on",
    "annotations" : [ "@com.fasterxml.jackson.annotation.JsonProperty(required = true)" ]
  }, {
    "name" : "options",
    "type" : "List<com.example.human.Choice>",
    "comment" : "required: List of options the human decision maker can select from",
    "annotations" : [ "@com.fasterxml.jackson.annotation.JsonProperty(required = true)" ]
  } ]
}
```

`Choice.d.json`:

```json
{
  "simpleName" : "Choice",
  "namespace" : "com.example.human",
  "fields" : [ {
    "name" : "title",
    "comment" : "Short title for the option at hand",
    "annotations" : [ "@com.fasterxml.jackson.annotation.JsonProperty(required = true)" ]
  }, {
    "name" : "description",
    "comment" : "Detailed explanation of the option"
  } ]
}
```

Process data of the main process:

```json
"fields" : [ {
  "name" : "result"
}, {
  "name" : "decision",
  "type" : "com.example.human.HumanDecision"
}, {
  "name" : "aiMemoryId",
  "comment" : "name convention: field holding the memory id of an ongoing AI conversation"
} ]
```

## Tool sub-process: AskUserTools.p.json

The tool throws the decision as an error attribute:

```json
{
  "id" : "19D9B41DA478DA79",
  "kind" : "CALLABLE_SUB",
  "config" : {
    "data" : "com.example.AskUserToolsData"
  },
  "elements" : [ {
      "id" : "f30",
      "type" : "CallSubStart",
      "name" : "askUserDecision(HumanDecision)",
      "config" : {
        "signature" : "askUserDecision",
        "input" : {
          "params" : [
            { "name" : "decision", "type" : "com.example.human.HumanDecision", "desc" : "required: the decision which should be done by the human user" }
          ],
          "map" : {
            "out.decision" : "param.decision"
          }
        },
        "result" : {
          "params" : [
            { "name" : "selected", "type" : "List<com.example.human.Choice>", "desc" : "the users preferred choice" }
          ],
          "map" : {
            "result.selected" : "in.selected"
          }
        }
      },
      "tags" : [
        "tool"
      ],
      "visual" : {
        "at" : { "x" : 144, "y" : 96 },
        "description" : "Ask the human user to decide between options. Use whenever a decision should not be made by the AI."
      },
      "connect" : [
        { "id" : "f31", "to" : "f32" }
      ]
    }, {
      "id" : "f32",
      "type" : "ErrorEnd",
      "name" : "human:decision",
      "config" : {
        "throws" : {
          "error" : "human:decision"
        },
        "code" : "error.setAttribute(\"decision\", in.decision);"
      },
      "visual" : {
        "at" : { "x" : 416, "y" : 96 },
        "icon" : "std:EscalationThrow"
      }
    } ]
}
```

## Main process: agent, boundary, user task, loop back

```json
{
  "id" : "f24",
  "type" : "ProgramInterface",
  "name" : "Assistant",
  "config" : {
    "javaClass" : "com.axonivy.utils.smart.workflow.AgenticProcessCall",
    "userConfig" : {
      "system" : "Strictly ask the user instead of making bold decisions. Present your requests as HumanDecision (question + options) via the askUserDecision tool.",
      "query" : "<%=in.request%>",
      "tools" : "askUserDecision",
      "resultType" : "String.class",
      "resultMapping" : "in.result"
    }
  },
  "visual" : { "at" : { "x" : 352, "y" : 224 } },
  "boundaries" : [ {
      "id" : "f32",
      "type" : "ErrorBoundaryEvent",
      "name" : "human:decision",
      "config" : {
        "errorCode" : "human:decision",
        "output" : {
          "map" : {
            "out" : "in",
            "out.decision" : "error.getAttribute(\"decision\") as com.example.human.HumanDecision"
          }
        }
      },
      "visual" : { "at" : { "x" : 384, "y" : 202 }, "icon" : "std:Escalation" },
      "connect" : [ { "id" : "f33", "to" : "f26" } ]
    } ],
  "connect" : [ { "id" : "f25", "to" : "f23" } ]
}, {
  "id" : "f26",
  "type" : "UserTask",
  "name" : "User decision",
  "config" : {
    "dialog" : "com.example.HumanDecisionDialog:start(com.example.human.HumanDecision)",
    "call" : {
      "map" : { "param.decision" : "in.decision" }
    },
    "task" : {
      "name" : "AI asks: <%=in.decision.question%>"
    },
    "output" : {
      "map" : { "out" : "in" },
      "code" : [
        "import com.axonivy.utils.smart.workflow.tools.human.DecisionMaker;",
        "",
        "new DecisionMaker(in.aiMemoryId).resolve(result.first.title);"
      ]
    }
  },
  "visual" : { "at" : { "x" : 352, "y" : 120 } },
  "connect" : [ { "id" : "f27", "to" : "f24" } ]
}
```

Notes:
- The `UserTask` connects **back to the agent element `f24`**, not to a new agent.
- On the resumed call, the agent sends "continue with my selection from the tool" instead of the original `query`, and keeps the original system message.
- The agent may call the tool several times. Each round goes through the boundary and the task again.
- The dialog (here `HumanDecisionDialog`) is your own Html Dialog. It shows `question`, lets the user pick from `options`, and returns the selection (`result.first`).

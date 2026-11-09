# Smart Workflow Configuration

## Artifacts

All artifacts share groupId `com.axonivy.utils.ai` and type `iar`. Use the same version for all of them.

| artifactId | Purpose |
|------------|---------|
| `smart-workflow` | Core: AgenticProcessCall, tools, guardrails, memory, observability. **Required.** |
| `smart-workflow-openai` | OpenAI provider (chat + embeddings) |
| `smart-workflow-azure-openai` | Azure OpenAI provider |
| `smart-workflow-gemini` | Google Gemini provider |
| `smart-workflow-anthropic` | Anthropic Claude provider |
| `smart-workflow-xai` | xAI Grok provider |
| `smart-workflow-ollama` | Ollama provider for local models (chat + embeddings) |
| `smart-workflow-opensearch-rag` | RAG with OpenSearch, see [rag.md](rag.md) |
| `smart-workflow-dashboard` | Governance dashboard: conversation history, token usage, anomalies |

A project needs `smart-workflow` plus **at least one provider**. Providers are found at runtime, so only installed providers can be selected.

```xml
<dependency>
  <groupId>com.axonivy.utils.ai</groupId>
  <artifactId>smart-workflow</artifactId>
  <version>VERSION</version>
  <type>iar</type>
</dependency>
<dependency>
  <groupId>com.axonivy.utils.ai</groupId>
  <artifactId>smart-workflow-openai</artifactId>
  <version>VERSION</version>
  <type>iar</type>
</dependency>
```

Add `smart-workflow-opensearch-rag` or `smart-workflow-dashboard` the same way when needed.

Never hardcode a version. Replace `VERSION` with the first one found:
1. The version of an existing `smart-workflow` dependency in any project `pom.xml` of the workspace.
2. The `<version>` of the smart-workflow library's own `pom.xml`, if it is in the workspace.
3. The `<parent>` version of the target project's `pom.xml` (the Axon Ivy engine version), as the `ivy-market-import` skill does.

## Choosing provider and model

How the provider is resolved:
1. The element's `provider` key: `OpenAI`, `AzureOpenAI`, `Gemini`, `Anthropic`, `xAI` or `Ollama` (exact spelling).
2. Otherwise the variable `AI.DefaultProvider`.
3. Otherwise `OpenAI`.

The model comes from the element's `model` key (a script expression, e.g. `"\"gpt-4.1-mini\""`). If it is empty, `AI.Providers.<Provider>.DefaultModel` applies. For Azure the "model" is the **deployment name**.

## Provider variables (`config/variables.yaml` of the application project)

Secrets use `#[password]` and `${decrypt:...}`. Leave a value blank to keep the provider's default. The model names in the comments are examples only; newer models work as well, and the user's requirements take precedence.

```yaml
Variables:
  AI:
    # [enum: OpenAI, AzureOpenAI, Gemini, xAI, Anthropic, Ollama]
    DefaultProvider: "OpenAI"
    Providers:
      OpenAI:
        #[password]
        APIKey: ${decrypt:}
        BaseUrl: ""                    # custom endpoint / proxy
        DefaultModel: "gpt-4.1-mini"   # e.g. gpt-4o, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-5
        DefaultEmbeddingModel: ""      # text-embedding-3-small | text-embedding-3-large | text-embedding-ada-002
      AzureOpenAI:
        Endpoint: "https://my-resource.openai.azure.com/"
        DefaultDeployment: "gpt-4-1-mini"
        Deployments:                   # one entry per deployment, kebab-case names
          gpt-4-1-mini:
            Model: gpt-4.1-mini
            #[password]
            APIKey: ${decrypt:}
      Gemini:
        #[password]
        APIKey: ${decrypt:}
        BaseUrl: ""
        DefaultModel: "gemini-2.5-flash"   # gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, ...
      Anthropic:
        #[password]
        APIKey: ${decrypt:}
        BaseUrl: ""                        # default https://api.anthropic.com/v1/
        DefaultModel: "claude-haiku-4-5"   # claude-opus-4-6, claude-sonnet-4-6, claude-sonnet-4-5, ...
      xAI:
        #[password]
        APIKey: ${decrypt:}
        BaseUrl: ""
        DefaultModel: "grok-4-1-fast"
      Ollama:
        BaseUrl: "http://localhost:11434"
        DefaultModel: "llama3.2"
        DefaultEmbeddingModel: "nomic-embed-text"
        TimeoutSeconds: "300"
```

Only add the blocks for the providers that are installed.

## Core variables (defined by smart-workflow, override in the app)

```yaml
Variables:
  AI:
    CircuitBreaker:
      Enabled: "false"          # "true" stops ALL agent calls, see guardrails.md
    Guardrails:
      DefaultInput: ""          # comma list: PromptInjectionInputGuardrail, AiPromptInjectionInputGuardrail, PiiMaskingGuardrail
      DefaultOutput: ""         # comma list: SensitiveDataOutputGuardrail, PiiMaskingGuardrail
      PromptInjection:
        Classifier:
          Provider: ""
          Model: ""             # use a cheap model, e.g. gpt-4.1-nano
          SystemPrompt: ""
          MinLength: "0"
    Tool:
      WebSearch:
        Engine: "duckduckgo"
        MaxResults: ""
        WhitelistDomains: ""    # comma list, empty = all
    RAG: {}                     # see rag.md
    Observability:
      CustomFields:
        Enabled: "true"         # marks tasks and cases with custom field aiAssisted=SMART_WORKFLOW
      Ivy:
        Enabled: ""             # "true" records the chat history (governance audit, dashboard)
      Openinference:
        Enabled: ""             # "true" emits OpenInference tracing spans (e.g. Arize Phoenix)
        HideInputMessages: ""
        HideOutputMessages: ""
```

## Observability and governance

- **Custom fields:** every task and case that runs an agent gets the string custom field `aiAssisted` = `SMART_WORKFLOW`. Use it to filter AI-assisted work in Portal or the cockpit.
- **Chat history:** with `AI.Observability.Ivy.Enabled: "true"`, each agent conversation (messages, tools, guardrail results, tokens) is stored per case and task. The `smart-workflow-dashboard` project visualizes it.
- **Tracing:** with `AI.Observability.Openinference.Enabled: "true"`, OpenInference spans are emitted. The Hide* flags remove message content from the spans.
- The agent's element `name` is used as the agent name in history and traces, so give every AgenticProcessCall a meaningful `name`.

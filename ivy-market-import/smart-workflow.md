# Smart Workflow — Item-Specific Instructions

Smart Workflow supports **multiple AI providers**. Before downloading, you must determine which providers the user needs.

## Step A — Read supported AI providers from README

Fetch the README of the smart-workflow repo to find the list of supported AI providers:

```
https://raw.githubusercontent.com/axonivy-market/smart-workflow/master/README.md
```

Extract all listed AI providers from the README (e.g. OpenAI, Azure OpenAI, Ollama, etc.).

## Step B — Ask the user which AI providers to support

Present the list of supported providers and ask:

> "Smart Workflow supports multiple AI providers. Which AI provider(s) would you like to use?
> Supported providers: **[list from README]**
>
> If you're not sure, I'll include all providers."

- If the user selects specific providers → note them for configuration guidance after import.
- If the user doesn't know or says "all" → proceed with the full download without filtering.

> This does not affect which IAR is downloaded — the smart-workflow IAR contains all providers. The choice informs which variables/connectors need to be configured after import.

## Step C — Continue with standard import

Proceed with Steps 1–5 of the standard ivy-market-import skill.

After Step 5, remind the user to configure the variables for their chosen AI provider(s) in `config/variables.yaml`.

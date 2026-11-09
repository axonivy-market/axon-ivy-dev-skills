# RAG with OpenSearch

Retrieval-Augmented Generation (RAG): index documents into an OpenSearch vector store, then let an agent answer from them through the `openSearchSearch` tool.

## Dependency

Add `smart-workflow-opensearch-rag` next to the core artifact, with the same version (see [configuration.md](configuration.md)).

**Embeddings are only supported by the `OpenAI` and `Ollama` providers.** At least one of them must be installed and configured, even if chat uses another provider.

## Variables

```yaml
Variables:
  AI:
    RAG:
      MaxResults: "5"          # segments returned per query
      MinScore: "0.6"          # cosine similarity threshold 0.0 - 1.0
      ChunkSize: "300"         # tokens per chunk when indexing
      ChunkOverlap: "20"       # overlapping tokens between chunks
      EmbeddingModel:
        Provider: ""           # OpenAI | Ollama; blank uses AI.DefaultProvider
        Name: ""               # e.g. text-embedding-3-small; blank uses the provider's DefaultEmbeddingModel
        ApiKey: ${decrypt:}    # optional separate key; blank uses the provider's API key
      OpenSearch:
        Url: "http://localhost:9200"
        ApiKey: ${decrypt:}    # or UserName/Password, or leave all blank when security is disabled
        UserName: ""
        Password: ${decrypt:}
        TrustSelfSignedCertificates: "false"   # true only for dev/test
```

**Use the same embedding model for indexing and searching.** The index stores which provider and model created it.

## 1. Index documents

Call the bundled sub-process `OpenSearchVectorStoreManagement:createVectorStore(String,List)`:

```json
{
  "id" : "f5",
  "type" : "SubProcessCall",
  "name" : "Index documents",
  "config" : {
    "processCall" : "OpenSearchVectorStoreManagement:createVectorStore(String,List)",
    "call" : {
      "map" : {
        "param.collection" : "\"hr-policies\"",
        "param.sources" : "in.documentTexts"
      }
    },
    "output" : {
      "map" : {
        "out.ragResult" : "result.result"
      }
    }
  },
  "visual" : { "at" : { "x" : 352, "y" : 64 } }
}
```

- `collection` is the OpenSearch index name.
- `sources` is a `List<String>` of **plain text**. Turn PDFs into text first, e.g. with an agent: `"system" : "Extract the complete text content from the PDF document. Return only the plain text."` and `"query" : "<%=in.pdfBinary%>"`.
- The result is `com.axonivy.utils.smart.workflow.rag.pipeline.RagResult`. `answer` holds "Indexed N segments.", and failures are reported in it as well.

From Java:

```java
import com.axonivy.utils.smart.workflow.rag.pipeline.internal.OpenSearchIngestor;

RagResult result = new OpenSearchIngestor().ingest("hr-policies", texts);
```

## 2. Answer questions with the agent

```json
"userConfig" : {
  "system" : "You are a RAG assistant.\nYou MUST always call the openSearchSearch tool before answering any question.\nUse the collection <%=in.indexName%>.\nBase your answer strictly on the retrieved documents.\nIf no relevant documents are found, clearly state that no relevant information was found in the knowledge base. Do not answer from your own knowledge.",
  "query" : "<%=in.question%>",
  "tools" : "openSearchSearch",
  "resultType" : "com.axonivy.utils.smart.workflow.rag.pipeline.RagResult.class",
  "resultMapping" : "in.ragResult"
}
```

`openSearchSearch` parameters, which the model fills in:
- `collection` (required): **put the index name in the system prompt.**
- `query`: the full user question.
- `maxResults` and `minScore`: optional. If missing, `AI.RAG.MaxResults` and `AI.RAG.MinScore` apply.

The result type can be `RagResult`, `String`, or your own answer class.

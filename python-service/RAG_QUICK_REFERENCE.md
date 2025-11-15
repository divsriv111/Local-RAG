# RAG Chain Quick Reference

## Quick Start

### Import and Initialize

```python
from services.rag_service import RAGService

rag = RAGService()
```

### Basic Query

```python
result = rag.query(
    query="Your question here",
    workspace_id="workspace-id",
    pdf_ids=["pdf-1", "pdf-2"],
    model_name="gpt-4-turbo",
    chat_history=None
)

print(result["answer"])
print(result["references"])
```

### Streaming Query

```python
for chunk in rag.query_stream(
    query="Your question",
    workspace_id="workspace-id",
    pdf_ids=["pdf-1"],
    model_name="gpt-4o-mini",
    chat_history=[]
):
    if chunk["type"] == "token":
        print(chunk["content"], end="")
    elif chunk["type"] == "done":
        print("\nReferences:", chunk["references"])
```

## Response Structure

### Non-Streaming Response

```json
{
  "answer": "Response with **markdown** and [Source: file.pdf, Page 5]",
  "references": [
    { "pdf": "file.pdf", "page": 5 },
    { "pdf": "other.pdf", "page": 10 }
  ],
  "model_used": "gpt-4-turbo",
  "processing_time_ms": 1234.56,
  "token_count": 150
}
```

### Streaming Chunks

```json
// Source reference
{"type": "source", "pdf": "file.pdf", "page": 5, "relevance_score": 0.89}

// Token
{"type": "token", "content": "word"}

// Final
{
  "type": "done",
  "answer": "complete response",
  "references": [...],
  "metadata": {"model_used": "...", "processing_time_ms": ..., "token_count": ...}
}

// Error
{"type": "error", "message": "error description"}
```

## Chat History Format

```python
chat_history = [
    {"role": "user", "content": "First question"},
    {"role": "assistant", "content": "First answer"},
    {"role": "user", "content": "Follow-up question"}
]
```

## Available Models

| Model Name      | Provider        | Speed  | Quality   | Use Case              |
| --------------- | --------------- | ------ | --------- | --------------------- |
| `gpt-4-turbo`   | OpenAI          | Medium | Excellent | Complex queries       |
| `gpt-4o-mini`   | OpenAI          | Fast   | Very Good | General queries       |
| `gpt-4.1-mini`  | OpenAI          | Fast   | Very Good | Alias for gpt-4o-mini |
| `local-llama-3` | Ollama/LMStudio | Varies | Good      | Privacy-focused       |
| `local-mistral` | Ollama/LMStudio | Varies | Good      | Privacy-focused       |

## Configuration Settings

```python
# config/settings.py
RETRIEVAL_TOP_K = 5          # Number of documents to retrieve
LLM_TEMPERATURE = 0.7        # Response creativity (0-1)
MAX_TOKENS = 2000            # Maximum response length
CHUNK_SIZE = 1000            # Document chunk size
CHUNK_OVERLAP = 200          # Overlap between chunks
```

## Citation Patterns

LLM should use these formats:

```
[Source: filename.pdf, Page 5]
[Source: filename.pdf, Page: 5]
(Source: filename.pdf, Page 5)
```

Extraction also supports:

```
[filename.pdf, Page 5]
[filename.pdf, p. 5]
```

## Common Operations

### Generate Chat Title

```python
title = rag.generate_chat_name("What is machine learning?")
# Returns: "Machine Learning Basics"
```

### Error Handling

```python
try:
    result = rag.query(...)
except Exception as e:
    print(f"Error: {e}")
```

### Streaming Error Handling

```python
for chunk in rag.query_stream(...):
    if chunk["type"] == "error":
        print(f"Error: {chunk['message']}")
        break
```

## Tips & Best Practices

✅ **DO:**

- Always provide workspace_id and pdf_ids
- Use streaming for better UX
- Include chat_history for follow-ups
- Monitor processing_time_ms
- Handle empty responses gracefully

❌ **DON'T:**

- Don't omit pdf_ids (will search all PDFs)
- Don't ignore error chunks in streaming
- Don't pass very long chat_history (uses last 5)
- Don't use high temperature for factual queries

## Performance Tuning

**Faster Responses:**

- Use `gpt-4o-mini` instead of `gpt-4-turbo`
- Reduce `RETRIEVAL_TOP_K` to 3
- Filter by specific PDF IDs

**Better Quality:**

- Use `gpt-4-turbo` for complex queries
- Increase `RETRIEVAL_TOP_K` to 7-10
- Use higher `MAX_TOKENS` for detailed answers

## Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Retrieved Documents

```python
from services.vector_store import VectorStoreManager

vector_store = VectorStoreManager()
docs = vector_store.similarity_search_with_score(
    query="test",
    workspace_id="ws-id",
    pdf_ids=["pdf-1"],
    k=5
)
print(f"Found {len(docs)} documents")
for doc, score in docs:
    print(f"  {doc.metadata['source']} (score: {score})")
```

### Test Model Availability

```python
from services.llm_service import LLMManager

llm_manager = LLMManager()
result = llm_manager.test_model_availability("gpt-4-turbo")
print(result)
```

## Integration with FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()
rag = RAGService()

@app.post("/query")
async def query_endpoint(request: dict):
    result = rag.query(
        query=request["query"],
        workspace_id=request["workspace_id"],
        pdf_ids=request["pdf_ids"],
        model_name=request["model_name"],
        chat_history=request.get("chat_history")
    )
    return result

@app.post("/query/stream")
async def query_stream_endpoint(request: dict):
    async def generate():
        for chunk in rag.query_stream(
            query=request["query"],
            workspace_id=request["workspace_id"],
            pdf_ids=request["pdf_ids"],
            model_name=request["model_name"],
            chat_history=request.get("chat_history")
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Common Issues

### Issue: No documents retrieved

**Solution:** Check if PDFs are uploaded and processed into vector store

### Issue: No citations in response

**Solution:** LLM may not follow format. Fallback uses retrieved docs automatically.

### Issue: Slow responses

**Solution:** Use faster model, reduce top-k, or filter by fewer PDFs

### Issue: Context too long error

**Solution:** Reduce CHUNK_SIZE or RETRIEVAL_TOP_K in settings

### Issue: Model not available

**Solution:** Check API keys (OpenAI) or service status (Ollama/LMStudio)

## Testing Examples

### Pytest Test

```python
def test_rag_query():
    rag = RAGService()
    result = rag.query(
        query="test query",
        workspace_id="test-ws",
        pdf_ids=["test-pdf"],
        model_name="gpt-4o-mini",
        chat_history=None
    )
    assert "answer" in result
    assert "references" in result
    assert result["model_used"] == "gpt-4o-mini"
```

### Load Test

```python
import time

for i in range(100):
    start = time.time()
    result = rag.query(...)
    elapsed = time.time() - start
    print(f"Query {i}: {elapsed:.2f}s")
```

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
VECTOR_DB_PATH=/data/chromadb
DEFAULT_LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
MAX_TOKENS=2000
RETRIEVAL_TOP_K=5
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
OLLAMA_BASE_URL=http://localhost:11434
```

## Further Reading

- [Full Documentation](RAG_CHAIN_IMPLEMENTATION.md)
- [Vector Store Guide](services/VECTOR_STORE_README.md)
- [LLM Service Documentation](LLM_SERVICE_IMPLEMENTATION.md)

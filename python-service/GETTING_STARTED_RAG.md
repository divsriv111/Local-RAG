# Getting Started with RAG Chain

## 🚀 Quick Start Guide

This guide will help you start using the RAG chain with source citations immediately.

---

## Prerequisites

✅ Python 3.11+  
✅ All dependencies installed (`pip install -r requirements.txt`)  
✅ Vector store configured (ChromaDB or Qdrant)  
✅ LLM API keys set (OpenAI or local models)

---

## Step 1: Environment Setup

Create `.env` file with required configuration:

```bash
# OpenAI (for GPT models)
OPENAI_API_KEY=sk-your-api-key-here

# Vector Database
VECTOR_DB_PATH=/data/chromadb
VECTOR_DB_TYPE=chromadb

# LLM Settings
DEFAULT_LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
MAX_TOKENS=2000

# Retrieval
RETRIEVAL_TOP_K=5

# Local Models (optional)
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Step 2: Import and Initialize

```python
from services.rag_service import RAGService

# Initialize RAG service
rag = RAGService()
```

That's it! The service automatically initializes:

- Vector store manager
- LLM manager
- All necessary configurations

---

## Step 3: Make Your First Query

### Simple Query (Non-Streaming)

```python
result = rag.query(
    query="What are the main features?",
    workspace_id="workspace-123",
    pdf_ids=["pdf-1", "pdf-2"],
    model_name="gpt-4o-mini",
    chat_history=None
)

print("Answer:", result["answer"])
print("References:", result["references"])
print("Processing Time:", result["processing_time_ms"], "ms")
```

**Output:**

```json
{
  "answer": "The main features include **AI-powered search**, real-time collaboration, and advanced analytics. [Source: features.pdf, Page 5]",
  "references": [{ "pdf": "features.pdf", "page": 5 }],
  "model_used": "gpt-4o-mini",
  "processing_time_ms": 1234.56,
  "token_count": 25
}
```

---

## Step 4: Try Streaming (Real-time Responses)

```python
print("Generating response...")

for chunk in rag.query_stream(
    query="Explain the installation process",
    workspace_id="workspace-123",
    pdf_ids=["manual-pdf"],
    model_name="gpt-4-turbo",
    chat_history=[]
):
    if chunk["type"] == "token":
        # Print tokens as they arrive
        print(chunk["content"], end="", flush=True)

    elif chunk["type"] == "done":
        # Print final references
        print("\n\nReferences:")
        for ref in chunk["references"]:
            print(f"  - {ref['pdf']}, Page {ref['page']}")
```

**Output:**

```
Generating response...
The installation process involves three simple steps. First, download the installer from [Source: manual.pdf, Page 3]...

References:
  - manual.pdf, Page 3
  - manual.pdf, Page 7
```

---

## Step 5: Add Conversation Context

```python
# Simulate a conversation
chat_history = [
    {"role": "user", "content": "What is this product?"},
    {"role": "assistant", "content": "This is an AI chatbot system [Source: overview.pdf, Page 1]"}
]

# Ask a follow-up question
result = rag.query(
    query="How does it work?",
    workspace_id="workspace-123",
    pdf_ids=["overview-pdf"],
    model_name="gpt-4-turbo",
    chat_history=chat_history  # Include conversation context
)

print(result["answer"])
```

The RAG service will:

1. Include the last 5 messages for context
2. Generate a contextually aware response
3. Cite sources appropriately

---

## Common Use Cases

### 1. Document Q&A

```python
result = rag.query(
    query="What are the system requirements?",
    workspace_id="workspace-docs",
    pdf_ids=["requirements-pdf"],
    model_name="gpt-4o-mini",
    chat_history=None
)
```

### 2. Multi-Document Search

```python
result = rag.query(
    query="Compare the two approaches",
    workspace_id="workspace-research",
    pdf_ids=["paper1-pdf", "paper2-pdf", "paper3-pdf"],
    model_name="gpt-4-turbo",
    chat_history=None
)
```

### 3. Technical Support Chat

```python
history = [
    {"role": "user", "content": "I'm getting an error"},
    {"role": "assistant", "content": "What error message do you see?"},
    {"role": "user", "content": "Connection timeout"}
]

result = rag.query(
    query="How do I fix this?",
    workspace_id="workspace-support",
    pdf_ids=["troubleshooting-pdf"],
    model_name="gpt-4-turbo",
    chat_history=history
)
```

### 4. Generate Chat Title

```python
# After user's first question
title = rag.generate_chat_name("How do I install Python on Windows?")
# Returns: "Python Installation Windows"
```

---

## Integration with FastAPI

### Basic Endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel
from services.rag_service import RAGService

app = FastAPI()
rag = RAGService()

class QueryRequest(BaseModel):
    query: str
    workspace_id: str
    pdf_ids: list[str]
    model_name: str
    chat_history: list[dict] | None = None

@app.post("/api/llm/query")
async def query_endpoint(request: QueryRequest):
    result = rag.query(
        query=request.query,
        workspace_id=request.workspace_id,
        pdf_ids=request.pdf_ids,
        model_name=request.model_name,
        chat_history=request.chat_history
    )
    return result
```

### Streaming Endpoint

```python
from fastapi.responses import StreamingResponse
import json

@app.post("/api/llm/query/stream")
async def query_stream_endpoint(request: QueryRequest):
    async def generate():
        for chunk in rag.query_stream(
            query=request.query,
            workspace_id=request.workspace_id,
            pdf_ids=request.pdf_ids,
            model_name=request.model_name,
            chat_history=request.chat_history
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

## Testing Your Setup

### 1. Health Check

```python
# Check if everything is configured correctly
from services.vector_store import VectorStoreManager
from services.llm_service import LLMManager

# Test vector store
vector_store = VectorStoreManager()
health = vector_store.health_check()
print("Vector Store:", health["status"])

# Test LLM
llm_manager = LLMManager()
result = llm_manager.test_model_availability("gpt-4o-mini")
print("LLM Available:", result["available"])
```

### 2. Simple Test Query

```python
# Test with minimal setup
result = rag.query(
    query="test",
    workspace_id="test-workspace",
    pdf_ids=["test-pdf"],
    model_name="gpt-4o-mini",
    chat_history=None
)

if "don't have any relevant information" in result["answer"]:
    print("✅ RAG service working (no documents found - expected for test)")
else:
    print("✅ RAG service working with documents")
```

---

## Troubleshooting

### Issue: ImportError or ModuleNotFoundError

```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not configured"

Add to `.env`:

```
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "No relevant documents found"

- Ensure PDFs are uploaded to vector store
- Check workspace_id and pdf_ids are correct
- Verify vector store has data:

```python
vector_store = VectorStoreManager()
size = vector_store.get_collection_size("your-workspace-id")
print(f"Documents in collection: {size}")
```

### Issue: Slow responses

- Use faster model: `gpt-4o-mini` instead of `gpt-4-turbo`
- Reduce retrieval count in settings
- Filter by specific PDFs

---

## Next Steps

1. **Read Full Documentation**: [RAG_CHAIN_IMPLEMENTATION.md](RAG_CHAIN_IMPLEMENTATION.md)
2. **Try Examples**: Run `python services/rag_service_examples.py`
3. **Customize Settings**: Edit `config/settings.py`
4. **Integrate with API**: Use FastAPI endpoints above
5. **Monitor Performance**: Check processing times and token counts

---

## Quick Reference

| Task            | Method                        | Time      |
| --------------- | ----------------------------- | --------- |
| Simple query    | `rag.query(...)`              | ~1-3s     |
| Streaming query | `rag.query_stream(...)`       | Real-time |
| Generate title  | `rag.generate_chat_name(...)` | ~1s       |
| With history    | Pass `chat_history` parameter | Same      |

| Model         | Speed  | Quality    | Cost   |
| ------------- | ------ | ---------- | ------ |
| gpt-4o-mini   | ⚡⚡⚡ | ⭐⭐⭐⭐   | 💰     |
| gpt-4-turbo   | ⚡⚡   | ⭐⭐⭐⭐⭐ | 💰💰💰 |
| local-llama-3 | ⚡     | ⭐⭐⭐     | Free   |

---

## Support & Resources

- **Full Documentation**: [RAG_CHAIN_IMPLEMENTATION.md](RAG_CHAIN_IMPLEMENTATION.md)
- **Quick Reference**: [RAG_QUICK_REFERENCE.md](RAG_QUICK_REFERENCE.md)
- **Examples**: [services/rag_service_examples.py](services/rag_service_examples.py)
- **Summary**: [RAG_IMPLEMENTATION_SUMMARY.md](RAG_IMPLEMENTATION_SUMMARY.md)

---

## Success! 🎉

You're now ready to use the RAG chain with source citations. Start with simple queries and gradually add more complexity as needed.

**Happy coding!** 🚀

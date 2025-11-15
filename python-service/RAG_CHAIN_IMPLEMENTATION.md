# RAG Chain Implementation with Source Citations

## Overview

This document describes the RAG (Retrieval-Augmented Generation) chain implementation that generates responses with source citations from PDF documents.

## Architecture

### Components

1. **RAGService** (`services/rag_service.py`)

   - Main orchestrator for RAG pipeline
   - Handles query processing and streaming
   - Manages citation extraction and response formatting

2. **VectorStoreManager** (`services/vector_store.py`)

   - Vector database operations (ChromaDB/Qdrant)
   - Document retrieval with similarity search
   - Metadata filtering by workspace and PDF IDs

3. **LLMManager** (`services/llm_service.py`)
   - Multi-model LLM support (OpenAI, Ollama, LMStudio)
   - Streaming and non-streaming response generation
   - Prompt template management

## RAG Pipeline Steps

### 1. Document Retrieval

```python
retrieved_docs = self.vector_store.similarity_search_with_score(
    query=query,
    workspace_id=workspace_id,
    pdf_ids=pdf_ids,
    k=self.retrieval_top_k  # Default: 5
)
```

**Process:**

- Searches vector database for relevant document chunks
- Filters by workspace and selected PDF IDs
- Returns top-k documents with relevance scores
- Documents include metadata: source (PDF filename), page number

### 2. Context Formatting

```python
context = self._format_context(retrieved_docs)
```

**Format:**

```
[Document 1 - Source: filename.pdf, Page 5]
<document content>

[Document 2 - Source: report.pdf, Page 12]
<document content>

...
```

**Purpose:**

- Structures retrieved documents for LLM consumption
- Includes source attribution for each chunk
- Enables LLM to generate proper citations

### 3. Chat History Formatting

```python
formatted_history = self._format_chat_history(chat_history)
```

**Format:**

```
User: <previous question>
Assistant: <previous answer>
User: <another question>
Assistant: <another answer>
```

**Features:**

- Includes last 5 messages from conversation
- Provides conversational context
- Falls back to "No previous conversation" if empty

### 4. Prompt Template

The exact prompt template used:

```
You are a helpful AI assistant. Answer the user's question based ONLY on the following context from PDF documents.
If the answer is not in the context, say "I don't have enough information to answer this question."

Context:
{context}

Previous conversation:
{chat_history}

User question: {query}

Instructions:
- Provide a detailed and accurate answer
- Cite sources using [Source: filename.pdf, Page X] format
- Use markdown for formatting (bold, italic, lists, code blocks)
- Include clickable references at the end

Answer:
```

**Key Features:**

- Clear instructions for grounding in context
- Explicit citation format requirement
- Markdown formatting guidance
- Fallback behavior for insufficient information

### 5. Response Generation

**Non-Streaming:**

```python
response_text = self.llm_manager.generate_response(
    query=query,
    context=context,
    model_name=model_name,
    chat_history=chat_history
)
```

**Streaming:**

```python
for token in self.llm_manager.generate_response_stream(...):
    accumulated_response += token
    yield {"type": "token", "content": token}
```

**Streaming Events:**

- `{"type": "source", "pdf": "file.pdf", "page": 5, "relevance_score": 0.89}` - Source references
- `{"type": "token", "content": "word"}` - Response tokens
- `{"type": "done", "answer": "...", "references": [...], "metadata": {...}}` - Final response

### 6. Citation Extraction

**Supported Citation Patterns:**

```python
# Primary format (recommended)
[Source: filename.pdf, Page 5]

# Alternative formats (also supported)
[Source: filename.pdf, Page: 5]
(Source: filename.pdf, Page 5)
[filename.pdf, Page 5]
[filename.pdf, p. 5]
```

**Extraction Algorithm:**

1. Parse response text using regex patterns
2. Extract PDF filename and page number
3. Deduplicate citations
4. Fallback to retrieved documents if no citations found

**Example Citation Extraction:**

```python
references = [
    {"pdf": "report.pdf", "page": 5},
    {"pdf": "manual.pdf", "page": 12},
    {"pdf": "guide.pdf", "page": 3}
]
```

### 7. Response Formatting

**Final Response Structure:**

```json
{
  "answer": "Markdown-formatted response with **bold**, *italic*, and citations [Source: file.pdf, Page 5]",
  "references": [
    { "pdf": "file.pdf", "page": 5 },
    { "pdf": "other.pdf", "page": 10 }
  ],
  "model_used": "gpt-4-turbo",
  "processing_time_ms": 1234.56,
  "token_count": 150
}
```

**Markdown Support:**

- **Bold text** using `**text**`
- _Italic text_ using `*text*`
- Lists (bullet and numbered)
- Code blocks using ```
- Links (auto-converted to clickable)
- Headers using `#`, `##`, etc.

## API Methods

### RAGService Class

#### `__init__()`

Initializes RAG service with vector store and LLM manager.

```python
def __init__(self):
    self.vector_store = VectorStoreManager()
    self.llm_manager = LLMManager()
    self.retrieval_top_k = settings.retrieval_top_k
```

#### `query()`

Process RAG query and generate complete response.

**Parameters:**

- `query` (str): User question
- `workspace_id` (str): Workspace identifier
- `pdf_ids` (List[str]): Selected PDF IDs to search
- `model_name` (str): LLM model to use
- `chat_history` (Optional[List[Dict]]): Previous messages

**Returns:**

```python
{
    "answer": str,
    "references": List[Dict],
    "model_used": str,
    "processing_time_ms": float,
    "token_count": int
}
```

**Example:**

```python
result = rag_service.query(
    query="What is machine learning?",
    workspace_id="workspace-123",
    pdf_ids=["pdf-1", "pdf-2"],
    model_name="gpt-4-turbo",
    chat_history=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
)
```

#### `query_stream()`

Process RAG query with streaming response.

**Parameters:** Same as `query()`

**Yields:**

```python
# Source reference
{"type": "source", "pdf": "file.pdf", "page": 5, "relevance_score": 0.89}

# Response token
{"type": "token", "content": "word"}

# Final completion
{
    "type": "done",
    "answer": "complete response",
    "references": [...],
    "metadata": {
        "model_used": "gpt-4-turbo",
        "processing_time_ms": 1234.56,
        "token_count": 150
    }
}

# Error (if occurs)
{"type": "error", "message": "error description"}
```

**Example:**

```python
for chunk in rag_service.query_stream(...):
    if chunk["type"] == "token":
        print(chunk["content"], end="", flush=True)
    elif chunk["type"] == "done":
        print("\n\nReferences:", chunk["references"])
```

#### `generate_chat_name()`

Generate concise chat title from first query.

**Parameters:**

- `first_query` (str): First user question

**Returns:**

- str: Chat title (3-5 words, max 50 chars)

**Example:**

```python
title = rag_service.generate_chat_name("How do neural networks work?")
# Returns: "Neural Networks Explained"
```

## Configuration

### Settings (config/settings.py)

```python
# Vector database
VECTOR_DB_PATH = "/data/chromadb"
RETRIEVAL_TOP_K = 5  # Number of documents to retrieve

# LLM settings
DEFAULT_LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 2000

# Document processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embeddings
EMBEDDING_MODEL = "text-embedding-ada-002"
USE_LOCAL_EMBEDDINGS = False
```

## Error Handling

### No Relevant Documents

```python
if not retrieved_docs:
    return {
        "answer": "I don't have any relevant information to answer this question.",
        "references": [],
        "model_used": model_name,
        "processing_time_ms": elapsed_time
    }
```

### LLM Generation Errors

```python
except Exception as e:
    logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
    raise  # Re-raise for FastAPI to handle
```

### Streaming Errors

```python
except Exception as e:
    yield {"type": "error", "message": str(e)}
```

## Performance Optimization

### 1. Document Retrieval

- Use metadata filters for faster queries
- Limit top-k to 5 for balance of relevance and speed
- Batch process embeddings

### 2. Response Generation

- Stream responses for better UX
- Cache LLM instances
- Use appropriate model (GPT-4o-mini for speed)

### 3. Citation Extraction

- Compile regex patterns once
- Deduplicate sources early
- Fallback to retrieved docs quickly

## Conversation Memory

### Memory Strategy

- **Buffer**: Last 5 messages from chat history
- **Format**: "User: ... \n Assistant: ..."
- **Purpose**: Maintain context for follow-up questions

### Implementation

```python
def _format_chat_history(self, chat_history: Optional[List[Dict]]) -> str:
    if not chat_history:
        return "No previous conversation."

    recent_history = chat_history[-5:]  # Last 5 messages
    history_lines = []

    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            history_lines.append(f"User: {content}")
        elif role == "assistant":
            history_lines.append(f"Assistant: {content}")

    return "\n".join(history_lines)
```

### Alternative: Conversation Summary Memory

For longer conversations, consider using LangChain's `ConversationSummaryMemory`:

```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=llm,
    max_token_limit=500
)
```

## Testing

### Unit Tests

```python
def test_citation_extraction():
    rag_service = RAGService()

    response = "The answer is in [Source: test.pdf, Page 5]"
    retrieved_docs = [
        (Document(page_content="...", metadata={"source": "test.pdf", "page": 5}), 0.9)
    ]

    references = rag_service._extract_citations(response, retrieved_docs)

    assert len(references) == 1
    assert references[0]["pdf"] == "test.pdf"
    assert references[0]["page"] == 5
```

### Integration Tests

```python
async def test_rag_query_stream():
    rag_service = RAGService()

    chunks = []
    async for chunk in rag_service.query_stream(
        query="Test query",
        workspace_id="test-workspace",
        pdf_ids=["test-pdf"],
        model_name="gpt-4o-mini",
        chat_history=[]
    ):
        chunks.append(chunk)

    assert any(c["type"] == "token" for c in chunks)
    assert any(c["type"] == "done" for c in chunks)
```

## Logging

All operations are logged with structured logging:

```python
logger.info(f"Processing RAG query for workspace {workspace_id}")
logger.info(f"Retrieving relevant documents...")
logger.info(f"Found {len(retrieved_docs)} relevant documents")
logger.info(f"Generating response with {model_name}...")
logger.info(f"Extracted {len(references)} citation references")
logger.info(f"RAG query completed in {processing_time:.2f}ms")
```

Errors are logged with full stack traces:

```python
logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
```

## Usage Examples

### 1. Basic Query

```python
from services.rag_service import RAGService

rag = RAGService()

result = rag.query(
    query="What are the key features?",
    workspace_id="ws-123",
    pdf_ids=["pdf-1", "pdf-2"],
    model_name="gpt-4-turbo",
    chat_history=None
)

print(result["answer"])
print("Sources:", result["references"])
```

### 2. Streaming Query

```python
for chunk in rag.query_stream(
    query="Explain the process",
    workspace_id="ws-123",
    pdf_ids=["pdf-1"],
    model_name="gpt-4o-mini",
    chat_history=[]
):
    if chunk["type"] == "token":
        print(chunk["content"], end="", flush=True)
```

### 3. With Chat History

```python
history = [
    {"role": "user", "content": "What is this about?"},
    {"role": "assistant", "content": "This document is about..."},
    {"role": "user", "content": "Tell me more"}
]

result = rag.query(
    query="Can you elaborate?",
    workspace_id="ws-123",
    pdf_ids=["pdf-1"],
    model_name="gpt-4-turbo",
    chat_history=history
)
```

## Best Practices

1. **Always provide PDF IDs** for focused retrieval
2. **Use streaming** for better user experience
3. **Include chat history** for conversational context
4. **Monitor token usage** to control costs
5. **Log all operations** for debugging
6. **Handle errors gracefully** with fallbacks
7. **Validate citations** before displaying to users
8. **Cache frequently accessed workspaces**

## Troubleshooting

### No Citations Generated

- Check if LLM response includes citation patterns
- Verify retrieved documents have source metadata
- Enable fallback to retrieved documents

### Incorrect Citations

- Validate citation regex patterns
- Check metadata format in vector store
- Ensure PDF filenames are correctly stored

### Slow Response Times

- Reduce retrieval_top_k value
- Use faster model (gpt-4o-mini)
- Enable caching for LLM instances

### Context Too Long

- Reduce chunk_size in document processing
- Limit number of retrieved documents
- Summarize chat history for long conversations

## Future Enhancements

1. **Re-ranking**: Add cross-encoder for better document ranking
2. **Hybrid Search**: Combine dense and sparse retrieval
3. **Multi-hop QA**: Support complex queries requiring multiple documents
4. **Citation Validation**: Verify citations match actual document content
5. **Adaptive Retrieval**: Dynamically adjust top-k based on query complexity
6. **Query Expansion**: Enhance user query with synonyms and related terms

## References

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [RAG Paper](https://arxiv.org/abs/2005.11401)

# Vector Store Quick Start Guide

## Installation

```bash
# Navigate to python-service directory
cd python-service

# Install dependencies
pip install -r requirements.txt
```

## Basic Setup

### 1. Configure Environment

Create or update `.env` file:

```bash
# Vector Database Type (chromadb or qdrant)
VECTOR_DB_TYPE=chromadb
VECTOR_DB_PATH=/data/chromadb

# Embeddings (choose one)
# Option 1: OpenAI (recommended for production)
OPENAI_API_KEY=sk-your-api-key-here
USE_LOCAL_EMBEDDINGS=False
EMBEDDING_MODEL=text-embedding-ada-002

# Option 2: Local HuggingFace (free, no API key needed)
# OPENAI_API_KEY=
# USE_LOCAL_EMBEDDINGS=True

# Retrieval Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=5
```

### 2. Simple Usage Example

```python
from services.vector_store import VectorStoreManager
from langchain.schema import Document

# Initialize vector store
vector_store = VectorStoreManager(db_type="chromadb")

# Create sample documents
documents = [
    Document(
        page_content="Python is a versatile programming language.",
        metadata={
            "source": "python_guide.pdf",
            "page": 1,
            "pdf_id": "python_guide"
        }
    )
]

# Add documents to workspace
workspace_id = "my-workspace-123"
success = vector_store.add_documents(
    documents=documents,
    workspace_id=workspace_id
)

print(f"Documents added: {success}")

# Search for relevant documents
results = vector_store.similarity_search(
    query="What is Python?",
    workspace_id=workspace_id,
    k=5
)

# Display results
for i, doc in enumerate(results, 1):
    print(f"\n{i}. {doc.page_content}")
    print(f"   Source: {doc.metadata.get('source')}")
    print(f"   Page: {doc.metadata.get('page')}")
```

## Common Use Cases

### 1. Adding PDFs to Workspace

```python
from services.pdf_processor import load_and_process_pdfs
from services.vector_store import VectorStoreManager

# Process PDFs
pdf_paths = [
    "/path/to/document1.pdf",
    "/path/to/document2.pdf"
]

documents = load_and_process_pdfs(pdf_paths, workspace_id)

# Store in vector database
vector_store = VectorStoreManager()
vector_store.add_documents(documents, workspace_id)
```

### 2. Searching with PDF Filters

```python
# Search only in specific PDFs
results = vector_store.similarity_search(
    query="machine learning algorithms",
    workspace_id="ws-123",
    pdf_ids=["ml_basics", "neural_networks"],  # Filter by these PDFs
    k=5
)
```

### 3. Getting Search Results with Scores

```python
# Get relevance scores
results_with_scores = vector_store.similarity_search_with_score(
    query="deep learning",
    workspace_id="ws-123",
    k=5
)

for doc, score in results_with_scores:
    print(f"Relevance: {score:.4f}")
    print(f"Content: {doc.page_content[:100]}...")
    print()
```

### 4. Async Operations (for FastAPI)

```python
import asyncio

async def search_documents():
    vector_store = VectorStoreManager()

    # Async search
    results = await vector_store.similarity_search_async(
        query="Python frameworks",
        workspace_id="ws-123",
        k=5
    )

    return results

# In FastAPI endpoint
@app.get("/search")
async def search(query: str, workspace_id: str):
    results = await search_documents()
    return {"results": results}
```

### 5. Managing Collections

```python
vector_store = VectorStoreManager()

# Get collection statistics
stats = vector_store.get_collection_stats("ws-123")
print(f"Documents: {stats['document_count']}")
print(f"Database: {stats['db_type']}")

# Delete workspace data
vector_store.delete_collection("ws-123")

# Clear cache
vector_store.clear_cache()
```

## Switching to Qdrant

### 1. Install Qdrant

```bash
pip install qdrant-client langchain-qdrant
```

### 2. Update Configuration

```python
# In .env
VECTOR_DB_TYPE=qdrant
VECTOR_DB_PATH=/data/qdrant
```

### 3. Use Hybrid Search

```python
vector_store = VectorStoreManager(db_type="qdrant")

# Hybrid search (dense + sparse)
results = vector_store.hybrid_search(
    query="neural networks",
    workspace_id="ws-123",
    k=5,
    sparse_weight=0.3  # Weight for sparse component
)
```

## Health Check

```python
# Check system health
health = vector_store.health_check()

print(f"Status: {health['status']}")
print(f"Database: {health['db_type']}")
print(f"Embedding model: {health['embedding_model']}")
print(f"Embedding test: {health['embedding_test']}")
print(f"Cached collections: {health['cached_collections']}")
```

## Testing

Run the comprehensive examples:

```bash
cd python-service/services
python vector_store_example.py
```

This will test:

- Document addition
- Similarity search
- Filtering by PDFs
- Batch operations
- Error handling
- Async operations

## Troubleshooting

### Issue: "Qdrant not available"

**Solution**: Install Qdrant dependencies or use ChromaDB

```bash
pip install qdrant-client langchain-qdrant
```

### Issue: "OpenAI API key not set"

**Solution**: Use local embeddings

```python
# In .env
USE_LOCAL_EMBEDDINGS=True
```

### Issue: Slow embedding generation

**Solution**:

1. Use OpenAI embeddings (faster)
2. Reduce document batch size
3. Use async operations

### Issue: No search results

**Solution**:

1. Verify documents were added successfully
2. Check workspace_id matches
3. Try without pdf_ids filter first
4. Verify collection exists: `get_collection_size()`

## Performance Tips

1. **Use batch processing** for multiple documents
2. **Filter by PDF IDs** to reduce search space
3. **Use async operations** in web applications
4. **Cache frequently accessed collections** (automatic)
5. **Monitor collection size** regularly
6. **Use Qdrant** for production/large scale

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure environment
3. ✅ Run test examples
4. ✅ Integrate with your application
5. ✅ Monitor performance
6. 📖 Read full documentation: `VECTOR_STORE_README.md`

## Integration with RAG Pipeline

```python
from services.vector_store import VectorStoreManager
from services.llm_service import LLMManager
from services.rag_service import RAGService

# Initialize components
vector_store = VectorStoreManager()
llm_manager = LLMManager()
rag_service = RAGService(vector_store, llm_manager)

# Process user query
response = rag_service.query(
    query="What is machine learning?",
    workspace_id="ws-123",
    pdf_ids=["ml_basics"],
    model_name="gpt-4o-mini"
)

print(response['answer'])
print(response['references'])
```

## Support

- **Documentation**: `services/VECTOR_STORE_README.md`
- **Examples**: `services/vector_store_example.py`
- **Summary**: `VECTOR_STORE_IMPLEMENTATION_SUMMARY.md`

---

**Ready to use!** Start by running the examples and then integrate into your RAG application.

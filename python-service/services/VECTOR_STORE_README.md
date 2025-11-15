# Vector Store Manager

Comprehensive vector database integration for storing and retrieving document embeddings with support for both ChromaDB and Qdrant.

## Features

- **Multi-Database Support**: ChromaDB (default) and Qdrant
- **Flexible Embeddings**: OpenAI or local HuggingFace embeddings
- **Metadata Filtering**: Filter by PDF IDs and workspace
- **Batch Processing**: Efficient handling of large document sets
- **Async Operations**: Non-blocking document operations
- **Hybrid Search**: Dense + sparse retrieval (Qdrant)
- **Collection Management**: Create, delete, and monitor collections
- **Performance Optimization**: Caching, connection pooling
- **Error Handling**: Graceful error recovery

## Installation

### ChromaDB (Default)

```bash
pip install chromadb langchain-community
```

### Qdrant (Optional)

```bash
pip install qdrant-client langchain-qdrant
```

### Embeddings

```bash
# For OpenAI embeddings
pip install langchain-openai

# For local HuggingFace embeddings
pip install langchain-huggingface sentence-transformers
```

## Quick Start

### Initialize Vector Store

```python
from services.vector_store import VectorStoreManager

# Using ChromaDB (default)
vector_store = VectorStoreManager(db_type="chromadb")

# Using Qdrant
vector_store = VectorStoreManager(db_type="qdrant")
```

### Add Documents

```python
from langchain.schema import Document

# Create documents with metadata
documents = [
    Document(
        page_content="Python is a programming language.",
        metadata={
            "source": "python_guide.pdf",
            "page": 1,
            "pdf_id": "python_guide"
        }
    ),
    Document(
        page_content="FastAPI is a web framework.",
        metadata={
            "source": "fastapi_docs.pdf",
            "page": 1,
            "pdf_id": "fastapi_docs"
        }
    )
]

# Add to workspace collection
workspace_id = "workspace-123"
success = vector_store.add_documents(
    documents=documents,
    workspace_id=workspace_id,
    batch_size=100
)
```

### Search Documents

```python
# Basic similarity search
results = vector_store.similarity_search(
    query="What is Python?",
    workspace_id=workspace_id,
    k=5
)

for doc in results:
    print(doc.page_content)
    print(doc.metadata)
```

### Filter by PDF IDs

```python
# Search within specific PDFs
results = vector_store.similarity_search(
    query="web framework",
    workspace_id=workspace_id,
    pdf_ids=["fastapi_docs", "django_guide"],
    k=5
)
```

### Search with Scores

```python
# Get relevance scores
results_with_scores = vector_store.similarity_search_with_score(
    query="machine learning",
    workspace_id=workspace_id,
    k=5
)

for doc, score in results_with_scores:
    print(f"Score: {score:.4f}")
    print(f"Content: {doc.page_content}")
```

## Async Operations

```python
import asyncio

async def process_documents():
    # Add documents asynchronously
    await vector_store.add_documents_async(
        documents=documents,
        workspace_id=workspace_id
    )

    # Search asynchronously
    results = await vector_store.similarity_search_async(
        query="What is AI?",
        workspace_id=workspace_id,
        k=5
    )

    return results

# Run async function
results = asyncio.run(process_documents())
```

## Collection Management

### Create/Get Collection

```python
# Automatically creates or retrieves collection
collection = vector_store.create_collection(workspace_id)
```

### Get Collection Stats

```python
stats = vector_store.get_collection_stats(workspace_id)
print(f"Documents: {stats['document_count']}")
print(f"Database: {stats['db_type']}")
print(f"Embedding model: {stats['embedding_model']}")
```

### Delete Collection

```python
# Remove workspace data
success = vector_store.delete_collection(workspace_id)
```

### Clear Cache

```python
# Clear in-memory collection cache
vector_store.clear_cache()
```

## Advanced Features

### Hybrid Search (Qdrant)

```python
# Dense + sparse retrieval
results = vector_store.hybrid_search(
    query="neural networks",
    workspace_id=workspace_id,
    k=5,
    sparse_weight=0.3
)
```

### Batch Operations

```python
# Process large document sets efficiently
large_documents = [...]  # 1000+ documents

success = vector_store.add_documents(
    documents=large_documents,
    workspace_id=workspace_id,
    batch_size=50  # Process 50 at a time
)
```

### Health Check

```python
health = vector_store.health_check()
print(f"Status: {health['status']}")
print(f"Embedding test: {health['embedding_test']}")
print(f"Cached collections: {health['cached_collections']}")
```

## Configuration

Set environment variables or update `config/settings.py`:

```python
# Vector Database
VECTOR_DB_TYPE=chromadb  # or qdrant
VECTOR_DB_PATH=/data/chromadb  # or /data/qdrant

# Embeddings
OPENAI_API_KEY=sk-...  # For OpenAI embeddings
USE_LOCAL_EMBEDDINGS=False  # True for HuggingFace
EMBEDDING_MODEL=text-embedding-ada-002

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=5
```

## Database Comparison

| Feature       | ChromaDB   | Qdrant     |
| ------------- | ---------- | ---------- |
| Setup         | Simple     | Simple     |
| Storage       | Local file | Local file |
| Performance   | Good       | Excellent  |
| Filtering     | Manual     | Native     |
| Hybrid Search | No         | Yes        |
| Scalability   | Good       | Excellent  |

## Metadata Structure

Each document should include:

```python
metadata = {
    "source": "filename.pdf",        # Required
    "page": 1,                        # Page number
    "pdf_id": "unique_pdf_id",       # For filtering
    "workspace_id": "workspace-123",  # Auto-added
    # Add custom fields as needed
}
```

## Performance Tips

1. **Batch Size**: Use 50-100 for optimal performance
2. **Caching**: Collections are cached automatically
3. **Async Operations**: Use for concurrent processing
4. **PDF Filtering**: Pre-filter with `pdf_ids` parameter
5. **Embedding Cache**: Embeddings are cached per query
6. **Connection Pooling**: Automatic for Qdrant

## Error Handling

All methods handle errors gracefully:

```python
# Returns empty list on error
results = vector_store.similarity_search(
    query="test",
    workspace_id="invalid",
    k=5
)
# results = []

# Returns False on error
success = vector_store.add_documents(
    documents=[],
    workspace_id="test"
)
# success = False
```

## Logging

All operations are logged:

```python
# View logs
import logging
logging.basicConfig(level=logging.INFO)

# Operations log:
# - Collection creation/loading
# - Document additions (with batch progress)
# - Search queries (with result counts)
# - Errors with stack traces
```

## Testing

Run the example file:

```bash
python services/vector_store_example.py
```

This demonstrates:

- ChromaDB and Qdrant usage
- Similarity search and filtering
- Batch operations
- Error handling
- Async operations

## Troubleshooting

### ChromaDB Issues

**Problem**: Collection not found

```python
# Solution: Create collection first
collection = vector_store.create_collection(workspace_id)
```

**Problem**: Slow embedding generation

```python
# Solution: Use local embeddings
# Set USE_LOCAL_EMBEDDINGS=True
```

### Qdrant Issues

**Problem**: Qdrant not available

```bash
# Solution: Install dependencies
pip install qdrant-client langchain-qdrant
```

**Problem**: Collection already exists error

```python
# Solution: Delete and recreate
vector_store.delete_collection(workspace_id)
collection = vector_store.create_collection(workspace_id)
```

### Embedding Issues

**Problem**: OpenAI API key not set

```python
# Solution: Use local embeddings or set key
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

**Problem**: HuggingFace model download fails

```bash
# Solution: Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"
```

## Migration Between Databases

### ChromaDB to Qdrant

```python
# 1. Initialize both stores
chroma_store = VectorStoreManager(db_type="chromadb")
qdrant_store = VectorStoreManager(db_type="qdrant")

# 2. Get documents from ChromaDB (pseudo-code)
# Note: You'll need to retrieve documents from your source
documents = get_documents_from_source()

# 3. Add to Qdrant
qdrant_store.add_documents(
    documents=documents,
    workspace_id=workspace_id
)

# 4. Verify migration
chroma_count = chroma_store.get_collection_size(workspace_id)
qdrant_count = qdrant_store.get_collection_size(workspace_id)
assert chroma_count == qdrant_count
```

## API Reference

### VectorStoreManager

**Constructor**

```python
VectorStoreManager(db_type: str = "chromadb")
```

**Methods**

- `create_collection(workspace_id: str)` - Create/get collection
- `add_documents(documents, workspace_id, batch_size=100)` - Add documents
- `add_documents_async(documents, workspace_id, batch_size=100)` - Add async
- `similarity_search(query, workspace_id, pdf_ids, k=5)` - Search
- `similarity_search_async(query, workspace_id, pdf_ids, k=5)` - Search async
- `similarity_search_with_score(query, workspace_id, pdf_ids, k=5)` - Search with scores
- `hybrid_search(query, workspace_id, pdf_ids, k=5, sparse_weight=0.3)` - Hybrid search
- `delete_collection(workspace_id)` - Delete collection
- `get_collection_size(workspace_id)` - Get document count
- `get_collection_stats(workspace_id)` - Get statistics
- `clear_cache()` - Clear collection cache
- `health_check()` - System health check

## Best Practices

1. **Use batch processing** for >100 documents
2. **Filter by PDF IDs** to reduce search space
3. **Use async operations** for concurrent requests
4. **Cache collections** (automatic)
5. **Monitor collection size** for performance
6. **Add metadata** for better filtering
7. **Handle errors gracefully** (methods return safe defaults)
8. **Use hybrid search** (Qdrant) for best results
9. **Clear cache** periodically in long-running services
10. **Health check** before critical operations

## License

MIT License - See LICENSE file for details

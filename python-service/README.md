# Python Service - RAG Chatbot LLM Microservice

FastAPI microservice for LLM interactions with RAG (Retrieval-Augmented Generation) pipeline.

## Features

- 🤖 **Multiple LLM Support**: OpenAI (GPT-4, GPT-4o-mini), Ollama, LMStudio
- 📚 **RAG Pipeline**: ChromaDB/Qdrant vector database with LangChain
- 📄 **PDF Processing**: Parse, chunk, and embed PDF documents
- 🔍 **Semantic Search**: Retrieve relevant document chunks
- 📝 **Source Citations**: Transparent references in responses
- 🌊 **Streaming Responses**: Real-time token streaming
- 📊 **Monitoring & Health Checks**: Comprehensive endpoint monitoring
- 🔍 **Distributed Tracing**: Correlation ID support
- 📈 **Metrics Export**: JSON and Prometheus formats

## Project Structure

```
python-service/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── config/
│   └── settings.py        # Configuration management
├── models/
│   ├── request_models.py  # Pydantic request models
│   └── response_models.py # Pydantic response models
├── services/
│   ├── llm_service.py     # LLM integration
│   ├── rag_service.py     # RAG pipeline
│   ├── pdf_processor.py   # PDF parsing and chunking
│   └── vector_store.py    # Vector database operations
├── utils/
│   ├── logger.py          # Logging configuration
│   └── monitoring.py      # Health checks and metrics
└── docs/
    ├── MONITORING_ENDPOINTS.md              # Monitoring API docs
    ├── MONITORING_IMPLEMENTATION_SUMMARY.md # Quick reference
    └── MONITORING_CHECKLIST.md              # Implementation checklist
```

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment**

```bash
cp .env.example .env
# Edit .env and set your API keys
```

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (for GPT models)

Optional but recommended:

- `VECTOR_DB_PATH`: Path for ChromaDB storage
- `UPLOAD_FOLDER`: Path for uploaded PDFs
- `ELASTICSEARCH_URL`: Elasticsearch for logging

### Run the Service

**Development mode:**

```bash
uvicorn main:app --reload --port 8000
```

**Production mode:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

**Using Python directly:**

```bash
python main.py
```

## API Endpoints

### Core Endpoints

#### `POST /api/llm/query`

Process LLM query with RAG pipeline (streaming).

**Request:**

```json
{
  "query": "What are the main findings?",
  "workspace_id": "workspace-123",
  "pdf_ids": ["pdf-001", "pdf-002"],
  "chat_history_id": "chat-001",
  "model_name": "gpt-4-turbo",
  "chat_history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi!" }
  ]
}
```

**Response:** Server-Sent Events (SSE) stream

```
data: {"type": "source", "pdf": "doc.pdf", "page": 5}
data: {"type": "token", "content": "The"}
data: {"type": "token", "content": " main"}
data: {"type": "done", "answer": "...", "references": [...]}
```

#### `POST /api/pdfs/process`

Process uploaded PDFs and add to vector store.

**Request:**

```json
{
  "workspace_id": "workspace-123",
  "pdf_ids": ["pdf-001", "pdf-002"]
}
```

**Response:**

```json
{
  "success": true,
  "documents_processed": 150,
  "pdfs_processed": 2
}
```

### Utility Endpoints

#### `GET /health`

Health check with component status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "checks": {
    "service": true,
    "vector_db": true,
    "llm": true
  },
  "version": "1.0.0"
}
```

#### `GET /api/models`

Get available LLM models.

**Response:**

```json
{
  "models": [
    { "name": "gpt-4-turbo", "status": "available", "provider": "openai" },
    { "name": "gpt-4o-mini", "status": "available", "provider": "openai" },
    { "name": "local-llama-3", "status": "available", "provider": "ollama" }
  ]
}
```

#### `POST /api/test-llm`

Test LLM connectivity.

**Request:**

```json
{
  "model_name": "gpt-4-turbo"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Model gpt-4-turbo is available",
  "latency_ms": 250.5,
  "model_name": "gpt-4-turbo"
}
```

#### `GET /metrics`

Get service metrics in JSON format.

**Response:**

```json
{
  "total_queries": 1250,
  "average_response_time_ms": 2500.5,
  "active_connections": 5,
  "memory_usage_mb": 512.3,
  "vector_db_size_mb": 1024.7,
  "uptime_seconds": 86400.0
}
```

#### `GET /metrics/prometheus`

Get service metrics in Prometheus format for scraping.

**Response:** Plain text in Prometheus exposition format

```
# HELP rag_total_queries Total number of queries processed
# TYPE rag_total_queries counter
rag_total_queries 1250
...
```

#### `POST /test-llm`

Test LLM connectivity by sending a simple query.

**Request:**

```json
{
  "model_name": "gpt-4-turbo"
}
```

**Response:**

```json
{
  "success": true,
  "response": "Hello! How can I assist you today?",
  "latency_ms": 150.5,
  "model_name": "gpt-4-turbo"
}
```

#### `GET /models`

Get list of available LLM models.

**Response:**

```json
{
  "models": [
    {
      "name": "gpt-4-turbo",
      "status": "available",
      "provider": "openai",
      "description": "GPT-4 Turbo Preview"
    }
  ]
}
```

### Monitoring Features

For complete monitoring documentation, see [MONITORING_ENDPOINTS.md](MONITORING_ENDPOINTS.md).

**Key Features:**

- ✅ Health checks for service, vector DB, and LLM
- ✅ Performance metrics (queries, latency, connections)
- ✅ Resource monitoring (memory, disk, CPU)
- ✅ Prometheus integration
- ✅ Distributed tracing with correlation IDs
- ✅ Centralized logging to Elasticsearch

## Configuration

All configuration is managed through environment variables (see `.env.example`).

### Key Settings

| Variable          | Default          | Description                              |
| ----------------- | ---------------- | ---------------------------------------- |
| `OPENAI_API_KEY`  | -                | OpenAI API key (required for GPT models) |
| `VECTOR_DB_PATH`  | `/data/chromadb` | Path for vector database storage         |
| `CHUNK_SIZE`      | `1000`           | Text chunk size for splitting            |
| `CHUNK_OVERLAP`   | `200`            | Overlap between chunks                   |
| `LLM_TEMPERATURE` | `0.7`            | LLM temperature (0.0-1.0)                |
| `MAX_TOKENS`      | `2000`           | Maximum tokens in response               |
| `RETRIEVAL_TOP_K` | `5`              | Number of documents to retrieve          |

## Local LLM Setup

### Using Ollama

1. **Install Ollama**

   ```bash
   curl https://ollama.ai/install.sh | sh
   ```

2. **Pull a model**

   ```bash
   ollama pull llama3
   ollama pull mistral
   ```

3. **Use in requests**
   ```json
   {
     "model_name": "local-llama-3",
     ...
   }
   ```

### Using LMStudio

1. **Download LMStudio** from https://lmstudio.ai/
2. **Load a model** in LMStudio
3. **Start the server** (port 1234 by default)
4. **Configure base URL** in `.env`:
   ```
   LOCAL_LLM_BASE_URL=http://localhost:1234/v1
   ```
5. **Use in requests**
   ```json
   {
     "model_name": "local-llama-3-lmstudio",
     ...
   }
   ```

## Development

### Project Dependencies

Core libraries:

- **FastAPI**: Web framework
- **LangChain**: LLM orchestration
- **ChromaDB**: Vector database
- **OpenAI**: GPT models
- **PyPDF**: PDF parsing

### Adding New Models

1. Add model configuration to `llm_service.py`
2. Implement model initialization in `get_llm()`
3. Add to available models list
4. Update documentation

### Testing

```bash
# Test health check
curl http://localhost:8000/health

# Test LLM
curl -X POST http://localhost:8000/api/test-llm \
  -H "Content-Type: application/json" \
  -d '{"model_name": "gpt-4o-mini"}'

# View API docs
open http://localhost:8000/docs
```

## Docker Deployment

See main project `docker-compose.yml` for containerized deployment.

**Build image:**

```bash
docker build -t rag-python-llm .
```

**Run container:**

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -v $(pwd)/data:/data \
  -v $(pwd)/uploads:/app/uploads \
  rag-python-llm
```

## Troubleshooting

**Import errors:**

```bash
pip install -r requirements.txt --upgrade
```

**ChromaDB errors:**

```bash
rm -rf /data/chromadb
# Restart service to reinitialize
```

**OpenAI API errors:**

- Check API key is valid
- Verify account has credits
- Check rate limits

**Out of memory:**

- Reduce `CHUNK_SIZE`
- Reduce `RETRIEVAL_TOP_K`
- Use smaller embedding model

## Logging

Logs are output to console and optionally to Elasticsearch.

**Configure Elasticsearch:**

```env
ELASTICSEARCH_URL=http://elasticsearch:9200
```

**Log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

**View logs:**

```bash
# Console logs
docker logs rag-python-llm

# Kibana (if configured)
open http://localhost:5601
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- GitHub Issues: https://github.com/your-org/rag-chatbot/issues
- Documentation: https://docs.your-domain.com

---

Built with FastAPI, LangChain, and ChromaDB

# Streaming LLM Endpoint - Quick Reference

## 📡 Endpoint

```
POST /api/llm/query
```

## 📤 Request

```json
{
  "query": "Your question here",
  "workspace_id": "workspace-uuid",
  "pdf_ids": ["pdf-001", "pdf-002"],
  "chat_history_id": "chat-uuid",
  "model_name": "gpt-4-turbo",
  "chat_history": [
    { "role": "user", "content": "Previous message" },
    { "role": "assistant", "content": "Previous response" }
  ]
}
```

## 📥 Response Format

### Headers

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Correlation-ID: uuid
```

### Chunk Types

#### 🔤 Token Chunk

```json
{ "type": "token", "content": "word" }
```

#### 📄 Source Chunk

```json
{ "type": "source", "pdf": "file.pdf", "page": 5, "relevance_score": 0.92 }
```

#### ✅ Done Chunk

```json
{
  "type": "done",
  "answer": "Complete answer...",
  "references": [{ "pdf": "file.pdf", "page": 5 }],
  "metadata": {
    "model_used": "gpt-4-turbo",
    "processing_time_ms": 2500,
    "token_count": 150
  }
}
```

#### ❌ Error Chunk

```json
{ "type": "error", "message": "Error description" }
```

## 🔧 Client Implementation

### TypeScript/Angular

```typescript
const response = await fetch("/api/llm/query", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  },
  body: JSON.stringify(request),
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value, { stream: true });
  const lines = text.split("\n");

  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const chunk = JSON.parse(line.substring(6));

      switch (chunk.type) {
        case "token":
          handleToken(chunk.content);
          break;
        case "source":
          handleSource(chunk);
          break;
        case "done":
          handleDone(chunk);
          return;
        case "error":
          handleError(chunk.message);
          return;
      }
    }
  }
}
```

### Python

```python
import requests
import json

response = requests.post(
    'http://localhost:8000/api/llm/query',
    json=request_data,
    headers={'Accept': 'text/event-stream'},
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b"data: "):
        chunk = json.loads(line[6:])

        if chunk['type'] == 'token':
            print(chunk['content'], end='', flush=True)
        elif chunk['type'] == 'done':
            break
```

### cURL

```bash
curl -N -X POST http://localhost:8000/api/llm/query \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"query":"Test","workspace_id":"test","pdf_ids":[],"chat_history_id":"test","model_name":"gpt-4o-mini","chat_history":[]}'
```

## 📊 Logging Fields

All logs include:

- `correlation_id` - Unique request ID
- `workspace_id` - Workspace identifier
- `model_name` - LLM model used
- `response_time_ms` - Processing time
- `token_count` - Tokens generated
- `retrieved_chunks` - Number of relevant documents

View in Kibana:

```
http://localhost:5601
Index: rag-chatbot-logs-*
```

## ⚙️ Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-your-key
DEFAULT_LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
MAX_TOKENS=2000
RETRIEVAL_TOP_K=5
CORS_ORIGINS=["http://localhost:4200"]
ELASTICSEARCH_URL=http://localhost:9200
```

### Supported Models

- `gpt-4-turbo` - GPT-4 Turbo Preview
- `gpt-4.1-mini` / `gpt-4o-mini` - GPT-4o Mini
- `local-llama-3` - LLaMA 3 (via Ollama/LMStudio)
- `local-mistral` - Mistral (via Ollama/LMStudio)

## 🐛 Troubleshooting

| Issue            | Solution                                       |
| ---------------- | ---------------------------------------------- |
| No response      | Check RAG service initialization and vector DB |
| Buffered/delayed | Verify `X-Accel-Buffering: no` header          |
| CORS errors      | Add frontend URL to `cors_origins`             |
| Timeout          | Increase client timeout to 5+ minutes          |
| Stream stops     | Check LLM API limits and logs                  |

## 📈 Monitoring

### Key Metrics

- **Query Start**: `level:INFO AND message:"Starting LLM query"`
- **Query Complete**: `level:INFO AND message:"LLM query completed"`
- **Errors**: `level:ERROR AND message:"Error in streaming"`
- **By Model**: `model_name:"gpt-4-turbo"`
- **Trace Request**: `correlation_id:"<uuid>"`

### Performance Tracking

Sort by `response_time_ms` (descending) to find slow queries.

## 🧪 Testing

```bash
# Install dependencies
pip install requests sseclient-py

# Run test script
python test_streaming.py

# Simple test (no SSE library)
python test_streaming.py simple
```

## 🔒 Security Checklist

- [ ] Add JWT authentication
- [ ] Implement rate limiting
- [ ] Validate user inputs
- [ ] Set resource limits
- [ ] Use HTTPS in production
- [ ] Secure API keys in vault
- [ ] Don't log sensitive data
- [ ] Restrict CORS origins

## 📚 Related Files

- `main.py` - FastAPI endpoint implementation
- `services/rag_service.py` - RAG pipeline with streaming
- `services/llm_service.py` - LLM integration
- `utils/logger.py` - Elasticsearch logging
- `config/settings.py` - Configuration
- `test_streaming.py` - Test script
- `STREAMING_ENDPOINT_GUIDE.md` - Full documentation

---

**Quick Test:**

```bash
# Start service
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test in another terminal
python test_streaming.py
```

**Need help?** Check logs at `http://localhost:5601` (Kibana)

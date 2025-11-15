# Monitoring and Health Check Endpoints

This document describes the health check and monitoring endpoints implemented in the Python LLM service.

## Overview

The service provides comprehensive monitoring capabilities through multiple endpoints that track service health, performance metrics, and system resources.

## Endpoints

### 1. Health Check Endpoint

**Endpoint:** `GET /health`

**Description:** Verifies the health of the service and its dependencies.

**Response Format:**

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

**Status Values:**

- `healthy`: All checks passed
- `degraded`: One or more checks failed

**Checks:**

- `service`: Always true if service is responding
- `vector_db`: Vector database (ChromaDB/Qdrant) connection status
- `llm`: LLM API availability (OpenAI or local models)

**Use Cases:**

- Container orchestration health checks
- Load balancer health probes
- Monitoring alerts and dashboards

---

### 2. Metrics Endpoint (JSON)

**Endpoint:** `GET /metrics`

**Description:** Returns comprehensive service metrics in JSON format.

**Response Format:**

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

**Metrics Included:**

- `total_queries`: Total number of queries processed since startup
- `average_response_time_ms`: Average response time in milliseconds
- `active_connections`: Current number of active HTTP connections
- `memory_usage_mb`: Process memory usage in megabytes
- `vector_db_size_mb`: Vector database storage size in megabytes
- `uptime_seconds`: Service uptime in seconds

**Additional Metrics (Extended):**
The underlying metrics collector also tracks:

- `p50_response_time_ms`: 50th percentile (median) response time
- `p95_response_time_ms`: 95th percentile response time
- `p99_response_time_ms`: 99th percentile response time
- `error_count`: Total number of errors
- `error_rate`: Error rate percentage
- System metrics: CPU usage, disk usage, etc.

---

### 3. Metrics Endpoint (Prometheus Format)

**Endpoint:** `GET /metrics/prometheus`

**Description:** Returns service metrics in Prometheus exposition format for scraping.

**Response Format (Plain Text):**

```
# HELP rag_total_queries Total number of queries processed
# TYPE rag_total_queries counter
rag_total_queries 1250

# HELP rag_response_time_seconds Average response time in seconds
# TYPE rag_response_time_seconds gauge
rag_response_time_seconds 2.5005

# HELP rag_active_connections Number of active connections
# TYPE rag_active_connections gauge
rag_active_connections 5

# ... (additional metrics)
```

**Prometheus Metrics:**

- `rag_total_queries` (counter): Total queries processed
- `rag_error_count` (counter): Total errors
- `rag_error_rate` (gauge): Error rate percentage
- `rag_response_time_seconds` (gauge): Average response time
- `rag_response_time_p50_seconds` (gauge): 50th percentile response time
- `rag_response_time_p95_seconds` (gauge): 95th percentile response time
- `rag_response_time_p99_seconds` (gauge): 99th percentile response time
- `rag_active_connections` (gauge): Active connections
- `rag_memory_usage_bytes` (gauge): Memory usage
- `rag_vector_db_size_bytes` (gauge): Vector DB size
- `rag_uptime_seconds` (counter): Service uptime

**Prometheus Configuration:**

```yaml
scrape_configs:
  - job_name: "rag-llm-service"
    static_configs:
      - targets: ["python-llm:8000"]
    metrics_path: "/metrics/prometheus"
    scrape_interval: 15s
```

---

### 4. Test LLM Endpoint

**Endpoint:** `POST /test-llm`

**Description:** Tests LLM connectivity by sending a simple query.

**Request Body:**

```json
{
  "model_name": "gpt-4-turbo"
}
```

**Response Format:**

```json
{
  "success": true,
  "response": "Hello! How can I assist you today?",
  "latency_ms": 150.5,
  "model_name": "gpt-4-turbo",
  "error": null
}
```

**Fields:**

- `success`: Whether the test was successful
- `response`: Truncated response from the model (first 50 characters)
- `latency_ms`: Response latency in milliseconds
- `model_name`: Model that was tested
- `error`: Error message if test failed (null if successful)

**Test Query:** The endpoint sends "Say 'Hello'" to verify model availability.

**Use Cases:**

- Verify LLM configuration
- Test model availability before sending actual queries
- Troubleshoot connection issues

---

### 5. Available Models Endpoint

**Endpoint:** `GET /models`

**Description:** Returns a list of available LLM models with their status.

**Response Format:**

```json
{
  "models": [
    {
      "name": "gpt-4-turbo",
      "status": "available",
      "provider": "openai",
      "description": "GPT-4 Turbo Preview"
    },
    {
      "name": "gpt-4o-mini",
      "status": "available",
      "provider": "openai",
      "description": "GPT-4o Mini"
    },
    {
      "name": "local-llama-3",
      "status": "available",
      "provider": "ollama/lmstudio",
      "description": "LLaMA 3 (via LMStudio or Ollama)"
    }
  ]
}
```

**Fields:**

- `name`: Model identifier used in query requests
- `status`: `available` or `unavailable`
- `provider`: Provider type (openai, ollama, lmstudio)
- `description`: Human-readable model description

**Status Logic:**

- OpenAI models: `available` if OPENAI_API_KEY is configured
- Local models: Assumes `available` (actual runtime check is expensive)

---

## Middleware Features

### Request Logging Middleware

All HTTP requests are logged with the following information:

**Request Log:**

```json
{
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "method": "POST",
  "path": "/api/llm/query",
  "client": "172.18.0.1",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response Log:**

```json
{
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "status_code": 200,
  "duration_ms": 2500.5,
  "timestamp": "2024-01-01T12:00:02Z"
}
```

### Correlation ID

Every request is assigned a correlation ID for distributed tracing:

- If client provides `X-Correlation-ID` header, it's used
- Otherwise, a new UUID is generated
- Correlation ID is returned in response headers
- All logs include the correlation ID
- Correlation ID is passed to downstream services

### Metrics Collection

The middleware automatically tracks:

- Active connections (incremented on request, decremented on completion)
- Query execution times (for `/api/llm/query` endpoint)
- Error counts (when exceptions occur)

---

## Error Handling

### Global Exception Handler

All uncaught exceptions are handled consistently:

**Error Response Format:**

```json
{
  "error": "Internal server error",
  "details": "Connection timeout to OpenAI API",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**HTTP Status Codes:**

- `422`: Validation error (invalid request body)
- `500`: Internal server error
- `503`: Service unavailable (dependencies not initialized)

### Validation Error Handler

Pydantic validation errors return detailed field-level errors:

```json
{
  "error": "Validation error",
  "details": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Monitoring Setup

### Docker Compose Integration

```yaml
services:
  python-llm:
    # ... service configuration
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Prometheus Integration

**prometheus.yml:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "rag-llm-service"
    static_configs:
      - targets: ["python-llm:8000"]
    metrics_path: "/metrics/prometheus"
```

### Grafana Dashboard

Key panels to include:

1. **Request Rate**: `rate(rag_total_queries[5m])`
2. **Error Rate**: `rag_error_rate`
3. **Response Time (P95)**: `rag_response_time_p95_seconds`
4. **Active Connections**: `rag_active_connections`
5. **Memory Usage**: `rag_memory_usage_bytes`
6. **Service Uptime**: `rag_uptime_seconds`

---

## Elasticsearch Logging

All logs are sent to Elasticsearch for centralized logging:

**Index Pattern:** `rag-chatbot-logs-*`

**Log Structure:**

```json
{
  "@timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "main",
  "message": "Request: POST /api/llm/query",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "method": "POST",
  "path": "/api/llm/query",
  "client": "172.18.0.1"
}
```

**Query Examples:**

Find all errors:

```json
GET /rag-chatbot-logs-*/_search
{
  "query": {
    "term": { "level": "ERROR" }
  }
}
```

Track requests by correlation ID:

```json
GET /rag-chatbot-logs-*/_search
{
  "query": {
    "term": { "correlation_id": "123e4567-e89b-12d3-a456-426614174000" }
  },
  "sort": [{ "@timestamp": "asc" }]
}
```

---

## Best Practices

### Health Checks

- Use `/health` for container orchestration health checks
- Set appropriate timeout values (10-30 seconds)
- Configure retries (3-5 attempts)
- Use startup period for initialization (30-60 seconds)

### Metrics Collection

- Scrape `/metrics/prometheus` every 15-30 seconds
- Monitor P95 and P99 response times for SLA compliance
- Set alerts on error rate thresholds (>1% errors)
- Track memory usage trends to detect leaks

### Logging

- Always include correlation ID in client requests
- Use correlation ID to trace requests across services
- Set up Elasticsearch alerts for ERROR and CRITICAL logs
- Implement log rotation and retention policies (30 days)

### Performance

- Metrics collection uses caching to avoid expensive computations
- Health checks perform minimal operations
- Middleware overhead is negligible (<1ms per request)
- Vector DB size calculation is cached in metrics

---

## Troubleshooting

### Service Not Healthy

**Symptom:** `/health` returns `degraded` status

**Checks:**

1. Review `checks` field to identify failing component
2. Check logs for error messages
3. Verify environment variables (API keys, paths)
4. Test individual components:
   - Vector DB: Check disk space, permissions
   - LLM: Verify API key, test with `/test-llm`

### High Response Times

**Symptom:** `average_response_time_ms` or P95 is high

**Actions:**

1. Check vector DB performance (query logs)
2. Verify LLM API latency with `/test-llm`
3. Review system metrics (CPU, memory, disk I/O)
4. Check active connections count

### Memory Growth

**Symptom:** `memory_usage_mb` continuously increases

**Actions:**

1. Check for unclosed connections
2. Review LLM cache size
3. Monitor vector DB memory usage
4. Consider implementing cache eviction policies

---

## API Client Examples

### Python Client

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
health = response.json()
print(f"Service status: {health['status']}")

# Get metrics
response = requests.get("http://localhost:8000/metrics")
metrics = response.json()
print(f"Total queries: {metrics['total_queries']}")

# Test LLM
response = requests.post(
    "http://localhost:8000/test-llm",
    json={"model_name": "gpt-4-turbo"}
)
test_result = response.json()
print(f"LLM available: {test_result['success']}")

# Get available models
response = requests.get("http://localhost:8000/models")
models = response.json()
for model in models['models']:
    print(f"{model['name']}: {model['status']}")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Metrics (JSON)
curl http://localhost:8000/metrics

# Metrics (Prometheus)
curl http://localhost:8000/metrics/prometheus

# Test LLM
curl -X POST http://localhost:8000/test-llm \
  -H "Content-Type: application/json" \
  -d '{"model_name": "gpt-4-turbo"}'

# Available models
curl http://localhost:8000/models

# With correlation ID
curl http://localhost:8000/health \
  -H "X-Correlation-ID: my-trace-id-123"
```

---

## Summary

The monitoring and health check endpoints provide comprehensive observability into the Python LLM service:

✅ **Health Checks:** Verify service and dependency status  
✅ **Metrics:** Track performance, resource usage, and errors  
✅ **Prometheus Support:** Native integration with Prometheus/Grafana  
✅ **Distributed Tracing:** Correlation IDs across all requests  
✅ **Centralized Logging:** Elasticsearch integration with structured logs  
✅ **Error Handling:** Consistent error responses and exception handling

These features enable effective monitoring, troubleshooting, and performance optimization of the RAG chatbot service.

# Streaming LLM Response Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAMING LLM ENDPOINT ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Angular    │
│   Frontend   │
│              │
│  fetch() API │
└──────┬───────┘
       │ POST /api/llm/query
       │ {query, workspace_id, pdf_ids, ...}
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI MAIN.PY                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  1. Middleware: Add Correlation ID                                           │
│     ├─ Generate UUID for request tracking                                    │
│     └─ Add to request.state.correlation_id                                   │
│                                                                               │
│  2. Request Validation (Pydantic)                                            │
│     ├─ Validate query, workspace_id, pdf_ids                                 │
│     ├─ Check model_name                                                      │
│     └─ Parse chat_history                                                    │
│                                                                               │
│  3. Log Query Start ──────────────────────┐                                  │
│     ├─ workspace_id, model_name           │                                  │
│     ├─ query_length, pdf_count            │                                  │
│     └─ correlation_id                     │                                  │
│                                           │                                  │
│  4. Call RAGService.query_stream()        │                                  │
│     │                                     │                                  │
│     └─────────────┐                       │                                  │
│                   ▼                       │                                  │
│     ┌──────────────────────────────────┐ │                                  │
│     │    RAG SERVICE                   │ │                                  │
│     ├──────────────────────────────────┤ │                                  │
│     │                                  │ │                                  │
│     │  A. Retrieve Documents           │ │                                  │
│     │     │                            │ │                                  │
│     │     ▼                            │ │                                  │
│     │  ┌────────────────────┐         │ │                                  │
│     │  │  VECTOR STORE      │         │ │                                  │
│     │  │  (ChromaDB/Qdrant) │         │ │                                  │
│     │  ├────────────────────┤         │ │                                  │
│     │  │ similarity_search  │         │ │                                  │
│     │  │ - Embed query      │         │ │                                  │
│     │  │ - Search vectors   │         │ │                                  │
│     │  │ - Return top-k     │         │ │                                  │
│     │  └────────────────────┘         │ │                                  │
│     │           │                     │ │                                  │
│     │           ▼                     │ │                                  │
│     │  Retrieved Docs (5)             │ │                                  │
│     │                                 │ │                                  │
│     │  B. Send Source Chunks ───────────┼─► yield {"type": "source"}      │
│     │     (Top 3 sources)             │ │                                  │
│     │                                 │ │                                  │
│     │  C. Format Context              │ │                                  │
│     │     - Combine doc contents      │ │                                  │
│     │     - Add source attribution    │ │                                  │
│     │     - Format chat history       │ │                                  │
│     │                                 │ │                                  │
│     │  D. Stream LLM Response         │ │                                  │
│     │     │                           │ │                                  │
│     │     ▼                           │ │                                  │
│     │  ┌────────────────────┐        │ │                                  │
│     │  │   LLM SERVICE      │        │ │                                  │
│     │  ├────────────────────┤        │ │                                  │
│     │  │ generate_response_ │        │ │                                  │
│     │  │     stream()       │        │ │                                  │
│     │  │                    │        │ │                                  │
│     │  │ ┌────────────────┐ │        │ │                                  │
│     │  │ │ OpenAI API /   │ │        │ │                                  │
│     │  │ │ Ollama /       │ │        │ │                                  │
│     │  │ │ LMStudio       │ │        │ │                                  │
│     │  │ └────────────────┘ │        │ │                                  │
│     │  │         │          │        │ │                                  │
│     │  │         ▼          │        │ │                                  │
│     │  │   Stream tokens    │        │ │                                  │
│     │  └────────────────────┘        │ │                                  │
│     │           │                    │ │                                  │
│     │           ▼                    │ │                                  │
│     │  for token in stream: ────────────┼─► yield {"type": "token"}      │
│     │                                │ │                                  │
│     │  E. Extract Citations          │ │                                  │
│     │     - Parse response text      │ │                                  │
│     │     - Find [Source: ...] tags  │ │                                  │
│     │     - Build references array   │ │                                  │
│     │                                │ │                                  │
│     │  F. Send Final Chunk ──────────────┼─► yield {"type": "done"}      │
│     │     - Complete answer          │ │                                  │
│     │     - References array         │ │                                  │
│     │     - Metadata                 │ │                                  │
│     │                                │ │                                  │
│     └────────────────────────────────┘ │                                  │
│                                        │                                  │
│  5. Exception Handling                 │                                  │
│     ├─ Catch any errors               │                                  │
│     ├─ Log error details              │                                  │
│     └─ yield {"type": "error"} ───────────────────────┐                  │
│                                        │               │                  │
│  6. Log Completion ────────────────────┤               │                  │
│     ├─ retrieved_chunks: N             │               │                  │
│     ├─ token_count: N                  │               │                  │
│     └─ response_time_ms: N             │               │                  │
│                                        │               │                  │
│  7. Update Metrics                     │               │                  │
│     └─ total_response_time += elapsed  │               │                  │
│                                        │               │                  │
└────────────────────────────────────────┼───────────────┼──────────────────┘
                                         │               │
                                         ▼               ▼
                          ┌──────────────────────────────────────┐
                          │         LOGGING PIPELINE             │
                          ├──────────────────────────────────────┤
                          │                                      │
                          │  Logger (utils/logger.py)            │
                          │    │                                 │
                          │    ├─ Console Handler               │
                          │    │    └─ stdout (development)     │
                          │    │                                 │
                          │    └─ Elasticsearch Handler         │
                          │         │                            │
                          │         ▼                            │
                          │  ┌─────────────────────┐            │
                          │  │  ELASTICSEARCH      │            │
                          │  │  (Port 9200)        │            │
                          │  ├─────────────────────┤            │
                          │  │ Index:              │            │
                          │  │ rag-chatbot-logs-*  │            │
                          │  │                     │            │
                          │  │ Fields:             │            │
                          │  │ - timestamp         │            │
                          │  │ - level             │            │
                          │  │ - message           │            │
                          │  │ - correlation_id    │            │
                          │  │ - workspace_id      │            │
                          │  │ - model_name        │            │
                          │  │ - response_time_ms  │            │
                          │  │ - token_count       │            │
                          │  └─────────────────────┘            │
                          │            │                         │
                          └────────────┼─────────────────────────┘
                                       │
                                       ▼
                          ┌──────────────────────────────────────┐
                          │         KIBANA DASHBOARD             │
                          │         (Port 5601)                  │
                          ├──────────────────────────────────────┤
                          │                                      │
                          │  • Query performance analytics       │
                          │  • Error tracking and alerts         │
                          │  • Model usage statistics            │
                          │  • Correlation ID trace viewer       │
                          │  • Real-time monitoring              │
                          │                                      │
                          └──────────────────────────────────────┘

                                       ▲
                                       │
                    ┌──────────────────┴───────────────────┐
                    │                                      │
            ┌───────┴──────┐                      ┌────────┴─────────┐
            │              │                      │                  │
            ▼              ▼                      ▼                  ▼
     data: {source}  data: {token}        data: {token}      data: {done}
            │              │                      │                  │
            └──────────────┴──────────────────────┴──────────────────┘
                                       │
                                       ▼
                          ┌──────────────────────────────────────┐
                          │      ANGULAR FRONTEND                │
                          ├──────────────────────────────────────┤
                          │                                      │
                          │  fetch().then(response => {          │
                          │    const reader = response.body      │
                          │      .getReader();                   │
                          │                                      │
                          │    while (true) {                    │
                          │      const {done, value} =           │
                          │        await reader.read();          │
                          │                                      │
                          │      // Parse SSE chunks             │
                          │      // Handle each type:            │
                          │      // - token  → append to UI      │
                          │      // - source → show reference    │
                          │      // - done   → complete          │
                          │      // - error  → show error        │
                          │    }                                 │
                          │  });                                 │
                          │                                      │
                          └──────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

TIMING DIAGRAM:

┌─────────┬─────────────────────────────────────────────────────────────────┐
│  Time   │  Event                                                          │
├─────────┼─────────────────────────────────────────────────────────────────┤
│ T+0ms   │  Frontend sends POST request                                    │
│ T+5ms   │  FastAPI receives, validates, logs query start                  │
│ T+10ms  │  Vector DB search begins                                        │
│ T+150ms │  Vector DB returns 5 relevant documents                         │
│ T+155ms │  Send 3 source chunks to frontend                               │
│ T+160ms │  Format context and build LLM prompt                            │
│ T+200ms │  LLM API call initiated                                         │
│ T+700ms │  First token received from LLM (first byte latency)             │
│ T+710ms │  Stream first token chunk to frontend                           │
│ T+720ms │  Stream second token chunk                                      │
│   ...   │  Continue streaming tokens (10-50 tokens/second)                │
│ T+3000ms│  Final token received from LLM                                  │
│ T+3005ms│  Extract citations from complete response                       │
│ T+3010ms│  Send done chunk with answer and references                     │
│ T+3015ms│  Log completion metrics to Elasticsearch                        │
│ T+3020ms│  Close stream, update global metrics                            │
└─────────┴─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

ERROR HANDLING FLOW:

Error Occurs
    │
    ├─ Exception caught in generate_stream()
    │
    ├─ Log error with full context:
    │   ├─ correlation_id
    │   ├─ workspace_id
    │   ├─ model_name
    │   ├─ error_type
    │   ├─ stack trace
    │   └─ elapsed time
    │
    ├─ Send error chunk to client:
    │   yield {"type": "error", "message": "..."}
    │
    ├─ Set error_occurred flag
    │
    └─ Finally block:
        ├─ Update metrics
        └─ Skip success logging

═══════════════════════════════════════════════════════════════════════════════

CHUNK TYPE SUMMARY:

┌─────────────────┬──────────────────────────────────────────────────────────┐
│ Chunk Type      │ Purpose                                                  │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ source          │ Show user where information comes from (before answer)   │
│                 │ Includes: pdf name, page number, relevance score         │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ token           │ Stream response text in real-time (as LLM generates)     │
│                 │ Includes: word or partial word                           │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ done            │ Signal completion with final answer and metadata         │
│                 │ Includes: complete answer, references, metrics           │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ error           │ Inform client of errors during processing                │
│                 │ Includes: error message (user-friendly)                  │
└─────────────────┴──────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
```

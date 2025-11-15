import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from config.settings import settings
from models.request_models import LLMQueryRequest, ProcessPDFRequest, TestLLMRequest
from models.response_models import (
    HealthResponse,
    ModelsResponse,
    MetricsResponse,
    ErrorResponse,
    StreamChunk
)
from services.rag_service import RAGService
from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStoreManager
from services.llm_service import LLMManager
from utils.logger import get_logger
from utils.monitoring import HealthChecker, metrics_collector

logger = get_logger(__name__)


# Global service instances
rag_service: Optional[RAGService] = None
pdf_processor: Optional[PDFProcessor] = None
vector_store: Optional[VectorStoreManager] = None
llm_manager: Optional[LLMManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global rag_service, pdf_processor, vector_store, llm_manager

    # Startup
    logger.info("Starting RAG Chatbot LLM Service...")

    try:
        # Initialize services
        rag_service = RAGService()
        pdf_processor = PDFProcessor()
        vector_store = VectorStoreManager()
        llm_manager = LLMManager()

        logger.info("All services initialized successfully")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down RAG Chatbot LLM Service...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "Content-Type", "X-Accel-Buffering"]
)


# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware for logging requests with method, path, duration, and correlation ID."""
    # Generate correlation ID from header or create new
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Track active connections
    metrics_collector.increment_connections()

    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }
    )

    start_time = time.time()

    try:
        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = (time.time() - start_time) * 1000

        # Record metrics for query endpoints
        if "/api/llm/query" in request.url.path:
            metrics_collector.record_query(duration / 1000)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Log response
        logger.info(
            f"Response: {response.status_code} in {duration:.2f}ms",
            extra={
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "duration_ms": round(duration, 2)
            }
        )

        return response

    except Exception as e:
        # Record error
        metrics_collector.record_error()

        logger.error(
            f"Request error: {str(e)}",
            extra={"correlation_id": correlation_id},
            exc_info=True
        )
        raise

    finally:
        metrics_collector.decrement_connections()


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status.
    - Checks if service is running
    - Verifies vector database connection
    - Tests LLM API availability (OpenAI ping)

    Returns:
        Service health status with component checks
    """
    checks = {
        "service": True,
        "vector_db": False,
        "llm": False
    }

    # Check vector database connection
    vector_db_check = HealthChecker.check_vector_db(vector_store)
    checks["vector_db"] = vector_db_check.get("healthy", False)

    # Check LLM API availability
    llm_check = HealthChecker.check_llm_api(
        llm_manager, settings.openai_api_key)
    checks["llm"] = llm_check.get("healthy", False)

    # Overall status
    status = "healthy" if all(checks.values()) else "degraded"

    logger.debug(f"Health check: {status} - {checks}")

    return HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        checks=checks,
        version=settings.api_version
    )


# LLM query endpoint with streaming
@app.post("/api/llm/query")
async def llm_query(request: LLMQueryRequest, http_request: Request):
    """
    Process LLM query with RAG pipeline and stream response in real-time.

    Streaming Format (Server-Sent Events):
    - Token chunk: {"type": "token", "content": "word"}
    - Source chunk: {"type": "source", "pdf": "file.pdf", "page": 3}
    - Final chunk: {"type": "done", "answer": "...", "references": [...]}
    - Error chunk: {"type": "error", "message": "..."}

    Args:
        request: LLM query request
        http_request: HTTP request for correlation ID

    Returns:
        StreamingResponse with text/event-stream content type
    """
    if not rag_service:
        raise HTTPException(
            status_code=503, detail="RAG service not initialized")

    # Get correlation ID from request
    correlation_id = getattr(
        http_request.state, 'correlation_id', str(uuid.uuid4()))

    # Log query start with detailed info
    logger.info(
        f"Starting LLM query - Workspace: {request.workspace_id}, Model: {request.model_name}, Query length: {len(request.query)}",
        extra={
            "correlation_id": correlation_id,
            "workspace_id": request.workspace_id,
            "model_name": request.model_name,
            "query_length": len(request.query),
            "pdf_count": len(request.pdf_ids),
            "chat_history_id": request.chat_history_id
        }
    )

    start_time = time.time()

    async def generate_stream():
        """Generate streaming response with proper SSE format."""
        retrieved_chunks_count = 0
        token_count = 0
        error_occurred = False

        try:
            for chunk in rag_service.query_stream(
                query=request.query,
                workspace_id=request.workspace_id,
                pdf_ids=request.pdf_ids,
                model_name=request.model_name,
                chat_history=request.chat_history
            ):
                # Track metrics
                chunk_type = chunk.get("type", "unknown")
                if chunk_type == "source":
                    retrieved_chunks_count += 1
                elif chunk_type == "token":
                    token_count += 1

                # Format as Server-Sent Event
                chunk_json = json.dumps(chunk)
                yield f"data: {chunk_json}\n\n"

            # Log successful completion
            elapsed = time.time() - start_time
            logger.info(
                f"LLM query completed - Model: {request.model_name}, "
                f"Retrieved chunks: {retrieved_chunks_count}, "
                f"Tokens: {token_count}, "
                f"Response time: {elapsed*1000:.2f}ms",
                extra={
                    "correlation_id": correlation_id,
                    "workspace_id": request.workspace_id,
                    "model_name": request.model_name,
                    "retrieved_chunks": retrieved_chunks_count,
                    "token_count": token_count,
                    "response_time_ms": elapsed * 1000
                }
            )

        except Exception as e:
            error_occurred = True
            elapsed = time.time() - start_time

            # Log error with full context
            logger.error(
                f"Error in streaming LLM query: {str(e)}",
                extra={
                    "correlation_id": correlation_id,
                    "workspace_id": request.workspace_id,
                    "model_name": request.model_name,
                    "error_type": type(e).__name__,
                    "response_time_ms": elapsed * 1000
                },
                exc_info=True
            )

            # Send error event to client
            error_chunk = {
                "type": "error",
                "message": f"An error occurred while generating the response: {str(e)}"
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"

        finally:
            # Final logging summary
            elapsed = time.time() - start_time
            if not error_occurred:
                logger.info(
                    f"Query session closed - Total time: {elapsed*1000:.2f}ms",
                    extra={
                        "correlation_id": correlation_id,
                        "total_time_ms": elapsed * 1000
                    }
                )

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Correlation-ID": correlation_id,
            "X-Accel-Buffering": "no",  # Disable buffering for nginx
        }
    )


# Process PDFs endpoint
@app.post("/api/pdfs/process")
async def process_pdfs(request: ProcessPDFRequest):
    """
    Process uploaded PDFs and add to vector store.

    Args:
        request: Process PDF request

    Returns:
        Success status
    """
    if not pdf_processor or not vector_store:
        raise HTTPException(status_code=503, detail="Services not initialized")

    try:
        logger.info(
            f"Processing {len(request.pdf_ids)} PDFs for workspace {request.workspace_id}")

        # Get PDF paths
        pdf_paths = pdf_processor.get_pdf_paths(
            request.workspace_id, request.pdf_ids)

        if not pdf_paths:
            raise HTTPException(
                status_code=404, detail="No valid PDF files found")

        # Process PDFs
        documents = pdf_processor.process_pdfs(
            pdf_paths=pdf_paths,
            workspace_id=request.workspace_id
        )

        if not documents:
            raise HTTPException(
                status_code=400, detail="Failed to process PDFs")

        # Add to vector store
        success = vector_store.add_documents(
            documents=documents,
            workspace_id=request.workspace_id
        )

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to add documents to vector store")

        return {
            "success": True,
            "documents_processed": len(documents),
            "pdfs_processed": len(pdf_paths)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Test LLM endpoint
@app.post("/test-llm")
async def test_llm(request: TestLLMRequest):
    """
    Test LLM connectivity and availability.
    Sends a simple query 'Say hello' to verify the model is working.

    Args:
        request: Test LLM request with model_name

    Returns:
        Test result with success status, response, and latency
    """
    if not llm_manager:
        raise HTTPException(
            status_code=503, detail="LLM service not initialized")

    try:
        start_time = time.time()

        # Test model with simple query
        test_result = llm_manager.test_model_availability(request.model_name)

        latency_ms = (time.time() - start_time) * 1000

        return {
            "success": test_result.get('available', False),
            "response": test_result.get('response', ''),
            "latency_ms": round(latency_ms, 2),
            "model_name": request.model_name,
            "error": test_result.get('error', None)
        }

    except Exception as e:
        logger.error(f"Error testing LLM: {str(e)}", exc_info=True)
        return {
            "success": False,
            "response": "",
            "latency_ms": 0,
            "model_name": request.model_name,
            "error": str(e)
        }


# Get available models endpoint
@app.get("/models", response_model=ModelsResponse)
async def get_models():
    """
    Get list of available LLM models.

    Returns:
        List of available models with status
    """
    if not llm_manager:
        raise HTTPException(
            status_code=503, detail="LLM service not initialized")

    try:
        models = llm_manager.get_available_models()
        return ModelsResponse(models=models)

    except Exception as e:
        logger.error(f"Error getting models: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Metrics endpoint (JSON format)
@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get service metrics in JSON format.

    Returns:
        Service metrics including:
        - Total queries processed
        - Average response time
        - Response time percentiles (p50, p95, p99)
        - Active connections
        - Memory usage
        - Vector database size
    """
    metrics = metrics_collector.get_metrics(settings.vector_db_path)

    return MetricsResponse(
        total_queries=metrics["total_queries"],
        average_response_time_ms=metrics["average_response_time_ms"],
        active_connections=metrics["active_connections"],
        memory_usage_mb=metrics.get("memory_mb", 0.0),
        vector_db_size_mb=metrics["vector_db_size_mb"],
        uptime_seconds=metrics["uptime_seconds"]
    )


# Metrics endpoint (Prometheus format)
@app.get("/metrics/prometheus")
async def get_metrics_prometheus():
    """
    Get service metrics in Prometheus exposition format.

    Returns:
        Plain text metrics in Prometheus format
    """
    prometheus_metrics = metrics_collector.get_prometheus_format(
        settings.vector_db_path)

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=prometheus_metrics,
        media_type="text/plain; version=0.0.4"
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )

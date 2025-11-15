from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class SourceReference(BaseModel):
    """Model for source reference in LLM response."""

    pdf: str = Field(..., description="PDF filename")
    page: int = Field(..., description="Page number")
    relevance_score: Optional[float] = Field(
        None, description="Relevance score from vector search")


class LLMQueryResponse(BaseModel):
    """Response model for LLM query."""

    answer: str = Field(..., description="Generated answer text")
    references: List[SourceReference] = Field(
        default_factory=list, description="Source references")
    model_used: str = Field(..., description="LLM model used for generation")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp")
    token_count: Optional[int] = Field(
        None, description="Number of tokens in response")
    processing_time_ms: Optional[float] = Field(
        None, description="Processing time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The main findings indicate...",
                "references": [
                    {"pdf": "research-paper.pdf",
                        "page": 5, "relevance_score": 0.92},
                    {"pdf": "research-paper.pdf",
                        "page": 12, "relevance_score": 0.87}
                ],
                "model_used": "gpt-4-turbo",
                "timestamp": "2024-01-01T12:00:00Z",
                "token_count": 150,
                "processing_time_ms": 2500.5
            }
        }


class StreamChunk(BaseModel):
    """Model for streaming response chunks."""

    type: str = Field(...,
                      description="Chunk type: token, source, metadata, done, error")
    content: Optional[str] = Field(
        None, description="Content for token chunks")
    pdf: Optional[str] = Field(None, description="PDF name for source chunks")
    page: Optional[int] = Field(
        None, description="Page number for source chunks")
    answer: Optional[str] = Field(
        None, description="Complete answer for done chunk")
    references: Optional[List[SourceReference]] = Field(
        None, description="References for done chunk")
    message: Optional[str] = Field(
        None, description="Error message for error chunks")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "examples": [
                {"type": "token", "content": "The"},
                {"type": "source", "pdf": "doc.pdf", "page": 5},
                {"type": "done", "answer": "Complete answer...", "references": []}
            ]
        }


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(...,
                        description="Service status: healthy or unhealthy")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Check timestamp")
    checks: Dict[str, bool] = Field(
        default_factory=dict, description="Individual health checks")
    version: str = Field(default="1.0.0", description="Service version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "checks": {
                    "vector_db": True,
                    "openai_api": True,
                    "elasticsearch": True
                },
                "version": "1.0.0"
            }
        }


class ModelInfo(BaseModel):
    """Model information."""

    name: str = Field(..., description="Model name")
    status: str = Field(..., description="Status: available or unavailable")
    provider: str = Field(...,
                          description="Provider: openai, ollama, lmstudio")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "gpt-4-turbo",
                "status": "available",
                "provider": "openai"
            }
        }


class ModelsResponse(BaseModel):
    """Response model for available models."""

    models: List[ModelInfo] = Field(
        default_factory=list, description="List of available models")

    class Config:
        json_schema_extra = {
            "example": {
                "models": [
                    {"name": "gpt-4-turbo", "status": "available",
                        "provider": "openai"},
                    {"name": "gpt-4o-mini", "status": "available",
                        "provider": "openai"},
                    {"name": "local-llama-3",
                        "status": "available", "provider": "ollama"}
                ]
            }
        }


class MetricsResponse(BaseModel):
    """Response model for service metrics."""

    total_queries: int = Field(
        default=0, description="Total queries processed")
    average_response_time_ms: float = Field(
        default=0.0, description="Average response time")
    active_connections: int = Field(
        default=0, description="Active connections")
    memory_usage_mb: float = Field(
        default=0.0, description="Memory usage in MB")
    vector_db_size_mb: float = Field(
        default=0.0, description="Vector database size in MB")
    uptime_seconds: float = Field(
        default=0.0, description="Service uptime in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "total_queries": 1250,
                "average_response_time_ms": 2500.5,
                "active_connections": 5,
                "memory_usage_mb": 512.3,
                "vector_db_size_mb": 1024.7,
                "uptime_seconds": 86400.0
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(
        None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "OpenAI API key not configured",
                "details": "Please set OPENAI_API_KEY in environment variables",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

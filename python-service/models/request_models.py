from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class LLMQueryRequest(BaseModel):
    """Request model for LLM query endpoint."""

    query: str = Field(..., description="User query to process",
                       min_length=1, max_length=5000)
    workspace_id: str = Field(...,
                              description="Workspace ID for document context")
    pdf_ids: List[str] = Field(...,
                               description="List of PDF document IDs to search")
    chat_history_id: str = Field(...,
                                 description="Chat history ID for conversation context")
    model_name: str = Field(default="gpt-4o-mini",
                            description="LLM model to use")
    chat_history: List[Dict[str, str]] = Field(
        default_factory=list, description="Previous conversation messages")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main findings in the research paper?",
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "pdf_ids": ["pdf-001", "pdf-002"],
                "chat_history_id": "chat-001",
                "model_name": "gpt-4-turbo",
                "chat_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help?"}
                ]
            }
        }


class PDFUploadRequest(BaseModel):
    """Request model for PDF upload."""

    workspace_id: str = Field(..., description="Workspace ID to upload PDF to")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class ProcessPDFRequest(BaseModel):
    """Request model for processing uploaded PDFs."""

    workspace_id: str = Field(..., description="Workspace ID")
    pdf_ids: List[str] = Field(..., description="List of PDF IDs to process")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "pdf_ids": ["pdf-001", "pdf-002"]
            }
        }


class TestLLMRequest(BaseModel):
    """Request model for testing LLM connectivity."""

    model_name: str = Field(default="gpt-4o-mini",
                            description="LLM model to test")

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "gpt-4-turbo"
            }
        }

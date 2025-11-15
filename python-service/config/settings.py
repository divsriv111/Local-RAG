from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = None

    # Vector Database Configuration
    vector_db_type: str = "chromadb"  # chromadb or qdrant
    vector_db_path: str = "/data/chromadb"

    # File Upload Configuration
    upload_folder: str = "/app/uploads"
    max_file_size_mb: int = 50

    # Document Processing Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Embedding Configuration
    # or sentence-transformers/all-mpnet-base-v2
    embedding_model: str = "text-embedding-ada-002"
    use_local_embeddings: bool = False  # Set to True to use HuggingFace embeddings

    # LLM Configuration
    default_llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7
    max_tokens: int = 2000

    # Local LLM Configuration (Ollama/LMStudio)
    local_llm_base_url: str = "http://localhost:1234/v1"  # LMStudio endpoint
    ollama_base_url: str = "http://localhost:11434"

    # Elasticsearch Configuration
    elasticsearch_url: Optional[str] = None
    elasticsearch_index_prefix: str = "rag-chatbot-logs"

    # API Configuration
    api_title: str = "RAG Chatbot LLM Service"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI microservice for LLM interactions and RAG pipeline"

    # CORS Configuration
    cors_origins: list[str] = [
        "http://localhost:4200", "http://localhost:5000"]

    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"

    # Retrieval Configuration
    retrieval_top_k: int = 5

    # Streaming Configuration
    stream_chunk_size: int = 1


# Create global settings instance
settings = Settings()

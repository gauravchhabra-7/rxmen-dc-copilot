"""
Configuration settings for RxMen Discovery Call Copilot Backend.

Loads environment variables and provides centralized configuration management.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All sensitive values should be stored in .env file (never committed to git).
    """

    # Application Settings
    app_name: str = "RxMen Discovery Call Copilot API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Settings (frontend URLs that can access this API)
    # NOTE: "null" allows file:// protocol for local HTML testing
    cors_origins: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080,null"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Claude API Settings
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # OpenAI API Settings (for embeddings)
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-3-small"

    # Pinecone Settings
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "rxmen-medical-knowledge"

    # RAG Settings
    rag_top_k: int = 8  # Number of chunks to retrieve (per handoff doc specification)
    rag_chunk_size: int = 800  # Target tokens per chunk (actual avg: 731 tokens)
    rag_chunk_overlap: int = 75  # Overlap between chunks (as implemented)

    # Data Paths
    medical_knowledge_path: str = "../data/extracted_text"

    # Logging
    log_level: str = "INFO"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

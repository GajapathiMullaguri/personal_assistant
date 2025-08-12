"""
Configuration management for the AI personal assistant.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Groq API Configuration
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    
    # Memory Configuration
    memory_persist_dir: Path = Field(
        default=Path("./data/memory"), 
        env="MEMORY_PERSIST_DIR"
    )
    memory_collection_name: str = Field(
        default="assistant_memories",
        env="MEMORY_COLLECTION_NAME"
    )
    memory_embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        env="MEMORY_EMBEDDING_MODEL"
    )
    memory_similarity_threshold: float = Field(
        default=0.7,
        env="MEMORY_SIMILARITY_THRESHOLD"
    )
    memory_max_results: int = Field(
        default=5,
        env="MEMORY_MAX_RESULTS"
    )
    
    # Application Configuration
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Streamlit Configuration
    streamlit_server_port: int = Field(default=8501, env="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(default="localhost", env="STREAMLIT_SERVER_ADDRESS")
    
    # LLM Configuration
    model_name: str = Field(default="llama3-8b-8192", env="GROQ_MODEL_NAME")
    temperature: float = Field(default=0.7, env="GROQ_TEMPERATURE")
    max_tokens: int = Field(default=4096, env="GROQ_MAX_TOKENS")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Allow extra fields from environment
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure memory directory exists
        self.memory_persist_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    """Base configuration for Language Models"""
    model_name: str
    model_type: str  # e.g., "openai", "anthropic", etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)  # temperature, max_tokens etc.

class EmbeddingConfig(BaseModel):
    """Configuration for embedding models"""
    model_name: str  # e.g., "text-embedding-ada-002"
    model_type: str  # e.g., "openai", "huggingface", etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DatabaseConfig(BaseModel):
    """Base configuration for Vector Stores"""
    database_type: str  # e.g., "chroma", "pinecone", etc.
    collection_name: str
    embedding: EmbeddingConfig 
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Database-specific parameters
    
class RetrieverConfig(BaseModel):
    """Base configuration for Retrievers"""
    search_type: str = "similarity"  # similarity, mmr, etc.
    k: int = 4
    search_parameters: Dict[str, Any] = Field(default_factory=dict)  # Additional parameters

class AgentConfig(BaseModel):
    """Complete agent configuration"""
    llm: LLMConfig
    retriever: RetrieverConfig
    database: DatabaseConfig
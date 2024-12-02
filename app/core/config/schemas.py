from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class LLMConfig(BaseModel):
    """Base configuration for Language Models"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., description="Name of the model")
    type: str = Field(..., description="Type of the model (e.g., openai, anthropic)")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters like temperature, max_tokens etc."
    )

class EmbeddingConfig(BaseModel):
    """Configuration for embedding models"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., description="Name of the embedding model")
    type: str = Field(..., description="Type of the model (e.g., openai, huggingface)")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for the embedding model"
    )

class DatabaseConfig(BaseModel):
    """Base configuration for Vector Stores"""
    database_type: str = Field(..., description="Type of vector store (e.g., chroma, pinecone)")
    collection_name: str = Field(..., description="Name of the collection")
    embedding: EmbeddingConfig = Field(..., description="Embedding model configuration")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Database-specific parameters"
    )
    
class RetrieverConfig(BaseModel):
    """Base configuration for Retrievers"""
    search_type: str = Field(
        default="similarity",
        description="Type of search (similarity, mmr, etc.)"
    )
    k: int = Field(default=4, description="Number of documents to retrieve")
    search_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional search parameters"
    )

class AgentConfig(BaseModel):
    """Complete agent configuration"""
    llm: LLMConfig = Field(..., description="Language model configuration")
    retriever: RetrieverConfig = Field(..., description="Retriever configuration")
    database: DatabaseConfig = Field(..., description="Vector store configuration")
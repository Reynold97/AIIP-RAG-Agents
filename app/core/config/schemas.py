from typing import Optional, Dict, Any
from pydantic import BaseModel

class LLMConfig(BaseModel):
    """Base state for Language Model configurations"""
    model_name: str
    model_type: str  # e.g., "openai", "anthropic", etc.
    parameters: Dict[str, Any] = {}  # Additional model parameters

class DatabaseConfig(BaseModel):
    """Base state for Database configurations"""
    database_name: str  # e.g., "ChromaDB", "Pinecone", etc.
    collection_name: str
    database_parameters: Dict[str, Any] = {}  # Additional database parameters
    search_parameters: Dict[str, Any] = {}  # Additional search parameters like k

class AgentConfig(BaseModel):
    """Base state for Agent configurations"""
    llm: LLMConfig
    database: DatabaseConfig
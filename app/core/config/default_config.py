from typing import Optional, Dict, Any, Literal
from .schemas import (
    LLMConfig,
    EmbeddingConfig,
    DatabaseConfig,
    RetrieverConfig,
    AgentConfig
)

# Available Language Models
AVAILABLE_LLMS: Dict[str, LLMConfig] = {
    "gpt-4o-mini": LLMConfig(
        name="gpt-4o-mini",
        type="openai",
        parameters={
            "temperature": 0.7,
        }
    ),
}

# Available Embedding Models
AVAILABLE_EMBEDDINGS: Dict[str, EmbeddingConfig] = {
    "text-embedding-3-small": EmbeddingConfig(
        name="text-embedding-3-small",
        type="openai",
        parameters={}
    ),
}

# Available Vector Stores
AVAILABLE_DATABASES = ["ChromaDB"]  # Add more as needed

# Available Search Types
AVAILABLE_SEARCH_TYPES = ["similarity", "mmr", "similarity_score_threshold"]

# Default Configurations
DEFAULT_LLM = AVAILABLE_LLMS["gpt-4o-mini"]

DEFAULT_EMBEDDING = AVAILABLE_EMBEDDINGS["text-embedding-3-small"]

DEFAULT_DATABASE = DatabaseConfig(
    database_type="ChromaDB",
    collection_name="default_collection",
    embedding=DEFAULT_EMBEDDING,
    parameters={
        "persist_directory": "./app/databases/chroma_db",
    }
)

DEFAULT_RETRIEVER = RetrieverConfig(
    collection_name="default_collection",
    search_type="similarity",
    k=4,
    search_parameters={}
)

DEFAULT_AGENT_CONFIG = AgentConfig(
    llm=DEFAULT_LLM,
    retriever=DEFAULT_RETRIEVER,
    agent_parameters={}
)

def get_llm_config(model_name: str) -> LLMConfig:
    """Get LLM configuration by model name"""
    if model_name not in AVAILABLE_LLMS:
        raise ValueError(f"Model {model_name} not found in available models")
    return AVAILABLE_LLMS[model_name]

def get_embedding_config(model_name: str) -> EmbeddingConfig:
    """Get embedding configuration by model name"""
    if model_name not in AVAILABLE_EMBEDDINGS:
        raise ValueError(f"Embedding model {model_name} not found in available models")
    return AVAILABLE_EMBEDDINGS[model_name]

def create_agent_config(
    llm_name: str = "gpt-4o-mini",
    collection_name: str = "default_collection",
    search_type: str = "similarity",
    k: int = 4,
    search_parameters: Optional[Dict[str, Any]] = None,
    agent_parameters: Optional[Dict[str, Any]] = None
) -> AgentConfig:
    """Create an agent configuration with specified parameters"""
    llm_config = get_llm_config(llm_name)
    
    retriever_config = RetrieverConfig(
        collection_name=collection_name,
        search_type=search_type,
        k=k,
        search_parameters=search_parameters or {}
    )
    
    return AgentConfig(
        llm=llm_config,
        retriever=retriever_config,
        agent_parameters=agent_parameters or {}
    )
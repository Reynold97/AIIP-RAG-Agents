from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from app.core.config.schemas import DatabaseConfig
from app.core.config.default_config import AVAILABLE_EMBEDDINGS, DEFAULT_DATABASE
from app.core.indexers.chroma_indexer import chroma_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chromadb", tags=["Database Operations"])

@router.post("/create", summary="Initialize or reconfigure ChromaDB")
async def create_database(
    config: Optional[DatabaseConfig] = Body(
        default=None,
        description="Database configuration. If not provided, default settings will be used.",
        example={
            "database_type": "ChromaDB",
            "collection_name": "default_collection",
            "embedding": {
                "name": "text-embedding-3-small",  # Changed from model_name
                "type": "openai",                  # Changed from model_type
                "parameters": {}
            },
            "parameters": {
                "collection_metadata": {"hnsw:space": "cosine"}
            }
        }
    )
):
    """
    Initialize or reconfigure ChromaDB with optional configuration.
    
    - If no config is provided, uses default settings
    - The persist_directory is fixed to './app/databases/chroma_db'
    - Supports different embedding models and collection metadata
    - This will affect all subsequent database operations
    """
    try:
        if config:
            # Ensure persist_directory is fixed
            config.parameters["persist_directory"] = DEFAULT_DATABASE.parameters["persist_directory"]
            # Reconfigure the global instance
            chroma_db.reconfigure(config)
        
        return {"message": "Database configured successfully", "config": config or DEFAULT_DATABASE}
    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/{collection_name}", summary="Create a new collection")
async def create_collection(collection_name: str):
    """Create a new collection using the current database configuration."""
    try:
        chroma_db.create_collection(collection_name)
        return {"message": f"Collection '{collection_name}' created successfully"}
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections", summary="List all collections")
async def list_collections():
    """List all available collections in the database."""
    try:
        collections = chroma_db.list_collections()
        return {"collections": collections}
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{collection_name}", summary="Delete a collection")
async def delete_collection(collection_name: str):
    """Delete a collection by name."""
    try:
        chroma_db.delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embeddings", summary="List available embedding models")
async def list_embeddings():
    """Get a list of all available embedding models and their configurations."""
    return {"embeddings": AVAILABLE_EMBEDDINGS}
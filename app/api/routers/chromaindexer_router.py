from fastapi import APIRouter, HTTPException, Body, File, UploadFile, Query
from typing import List, Optional
from app.core.indexers.chroma_indexer import ChromaIndexer
from app.core.pipes.simple_index_pipeline import SimpleIndexChromaPipeline
from app.core.config.schemas import RetrieverConfig
from langchain_core.documents import Document
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chroma", tags=["Index Operations"])

@router.post("/{collection_name}/add_documents", summary="Add documents to collection")
async def add_documents(
    collection_name: str,
    documents: List[dict] = Body(
        ..., 
        description="List of documents with page_content and metadata"
    )
):
    """
    Add documents to a collection.
    
    - Documents should include page_content and optional metadata
    - Uses the current database configuration
    """
    try:
        indexer = ChromaIndexer(collection_name)
        docs = [Document(**doc) for doc in documents]
        indexer.add_documents(docs)
        return {"message": f"{len(docs)} documents added to collection '{collection_name}'"}
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection_name}/search", summary="Search documents in collection")
async def search_documents(
    collection_name: str,
    query: str = Query(..., description="Search query"),
    retriever_config: Optional[RetrieverConfig] = Body(
        default=None,
        description="""Optional retriever configuration.
        Available search types: similarity, mmr, similarity_score_threshold.
        MMR parameters: fetch_k, lambda_mult.
        Similarity threshold parameters: score_threshold.""",
        example={
            "search_type": "similarity",
            "k": 4,
        }
    )
):
    """
    Search documents in a collection.
    
    - Supports different search types: similarity, mmr, similarity_score_threshold
    - MMR (Maximal Marginal Relevance) helps with result diversity
    - Similarity threshold allows filtering by minimum score
    """
    try:
        indexer = ChromaIndexer(collection_name)
        results = indexer.similarity_search(query, retriever_config)
        return {"results": [doc.dict() for doc in results]}
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{collection_name}/documents/{document_id}", summary="Delete a document")
async def delete_document(collection_name: str, document_id: str):
    """Delete a document from the collection by ID."""
    try:
        indexer = ChromaIndexer(collection_name)
        indexer.delete_document(document_id)
        return {"message": f"Document '{document_id}' deleted from collection '{collection_name}'"}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{collection_name}/documents/{document_id}", summary="Update a document")
async def update_document(
    collection_name: str,
    document_id: str,
    document: dict = Body(..., description="Document with page_content and metadata")
):
    """Update a document in the collection by ID."""
    try:
        indexer = ChromaIndexer(collection_name)
        doc = Document(**document)
        indexer.update_document(document_id, doc)
        return {"message": f"Document '{document_id}' updated in collection '{collection_name}'"}
    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collection_name}/count", summary="Count documents in collection")
async def count_documents(collection_name: str):
    """Get the total number of documents in a collection."""
    try:
        indexer = ChromaIndexer(collection_name)
        count = indexer.count_documents()
        return {"count": count}
    except Exception as e:
        logger.error(f"Error counting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection_name}/process_pdfs", summary="Process and index PDF files")
async def process_pdfs(
    collection_name: str,
    files: List[UploadFile] = File(..., description="PDF files to process")
):
    """
    Process PDF files and add their content to the collection.
    
    - Supports multiple PDF files
    - Automatically chunks content into appropriate sizes
    - Uses the current database configuration
    """
    try:
        pipeline = SimpleIndexChromaPipeline(collection_name)
        processed_docs = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                temp_file_path = os.path.join(temp_dir, file.filename)
                with open(temp_file_path, "wb") as buffer:
                    buffer.write(await file.read())
                processed_docs.extend(pipeline.process_pdf(temp_file_path))
        
        return {
            "message": f"{len(processed_docs)} documents processed and added to collection '{collection_name}'",
            "processed_files": [file.filename for file in files]
        }
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection_name}/process_folder", summary="Process and index folder of PDFs")
async def process_folder(
    collection_name: str,
    folder_path: str = Body(..., embed=True, description="Path to folder containing PDF files")
):
    """
    Process all PDF files in a folder and add their content to the collection.
    
    - Processes all PDFs in the specified folder
    - Automatically chunks content into appropriate sizes
    - Uses the current database configuration
    """
    try:
        pipeline = SimpleIndexChromaPipeline(collection_name)
        processed_docs = pipeline.process_folder(folder_path)
        
        return {
            "message": f"{len(processed_docs)} documents processed and added to collection '{collection_name}'",
            "folder_path": folder_path
        }
    except Exception as e:
        logger.error(f"Error processing folder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
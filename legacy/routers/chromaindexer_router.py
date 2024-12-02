from fastapi import APIRouter, HTTPException, Body, File, UploadFile
from typing import List
from app.core.indexers.chroma_indexer import ChromaIndexer
from app.core.pipes.simple_index_pipeline import SimpleIndexChromaPipeline
from langchain_core.documents import Document
import tempfile
import os

router = APIRouter(prefix="/chroma", tags=["Chroma Index Operations"])

# Original Indexer Endpoints

@router.post("/{collection_name}/add_documents")
async def add_documents(collection_name: str, documents: List[dict] = Body(...)):
    try:
        indexer = ChromaIndexer(collection_name)
        docs = [Document(**doc) for doc in documents]
        indexer.add_documents(docs)
        return {"message": f"{len(docs)} documents added to collection '{collection_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collection_name}/search")
async def search_documents(collection_name: str, query: str, k: int = 4):
    try:
        indexer = ChromaIndexer(collection_name)
        results = indexer.similarity_search(query, k)
        return {"results": [doc.dict() for doc in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{collection_name}/documents/{document_id}")
async def delete_document(collection_name: str, document_id: str):
    try:
        indexer = ChromaIndexer(collection_name)
        indexer.delete_document(document_id)
        return {"message": f"Document '{document_id}' deleted from collection '{collection_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{collection_name}/documents/{document_id}")
async def update_document(collection_name: str, document_id: str, document: dict = Body(...)):
    try:
        indexer = ChromaIndexer(collection_name)
        doc = Document(**document)
        indexer.update_document(document_id, doc)
        return {"message": f"Document '{document_id}' updated in collection '{collection_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collection_name}/count")
async def count_documents(collection_name: str):
    try:
        indexer = ChromaIndexer(collection_name)
        count = indexer.count_documents()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pipeline Processing Endpoints

@router.post("/{collection_name}/process_pdfs")
async def process_pdfs(collection_name: str, files: List[UploadFile] = File(...)):
    try:
        pipeline = SimpleIndexChromaPipeline(collection_name)
        processed_docs = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                temp_file_path = os.path.join(temp_dir, file.filename)
                with open(temp_file_path, "wb") as buffer:
                    buffer.write(await file.read())
                processed_docs.extend(pipeline.process_pdf(temp_file_path))
        
        return {"message": f"{len(processed_docs)} documents processed and added to collection '{collection_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection_name}/process_folder")
async def process_folder(collection_name: str, folder_path: str = Body(..., embed=True)):
    try:
        pipeline = SimpleIndexChromaPipeline(collection_name)
        processed_docs = pipeline.process_folder(folder_path)
        return {"message": f"{len(processed_docs)} documents processed and added to collection '{collection_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
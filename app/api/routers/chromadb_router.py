from fastapi import APIRouter, HTTPException
from app.databases.chroma_db import chroma_db

router = APIRouter(prefix="/chromadb", tags=["Databases"])

@router.post("/create")
async def create_database():
    try:
        chroma_db.initialize_db()
        return {"message": "Database created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete")
async def delete_database():
    try:
        chroma_db.delete_db()
        return {"message": "Database deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/{collection_name}")
async def create_collection(collection_name: str):
    try:
        chroma_db.create_collection(collection_name)
        return {"message": f"Collection '{collection_name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        chroma_db.delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections")
async def list_collections():
    try:
        collections = chroma_db.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
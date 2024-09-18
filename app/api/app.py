from fastapi import FastAPI
from app.api.routers import download_router, chromadb_router, chromaindexer_router, chromaagent_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(download_router.router)
app.include_router(chromadb_router.router)
app.include_router(chromaindexer_router.router)
app.include_router(chromaagent_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to AIIP AI Agents"}
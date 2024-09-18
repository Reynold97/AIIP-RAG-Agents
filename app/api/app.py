from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.loaders.gdrive_loader import router as download_router

load_dotenv()

app = FastAPI()

# Include the download router
app.include_router(download_router)

@app.get("/")
def root():
    return {"message": "Welcome to AIIP AI Agents"}

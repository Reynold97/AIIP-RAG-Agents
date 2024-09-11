from fastapi import FastAPI
from dotenv import load_dotenv
from data_ops.download import router as download_router

load_dotenv()

app = FastAPI()

# Include the download router
app.include_router(download_router)

@app.get("/")
def root():
    return {"message": "Welcome to AIIP AI Agents"}

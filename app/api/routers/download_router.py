from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.core.loaders.gdrive_loader import GDriveLoader

router = APIRouter(prefix="/gdrive", tags=["Google Drive"])

gdrive_loader = GDriveLoader()

@router.get("/authorize")
async def authorize():
    authorization_url, _ = gdrive_loader.authenticate()
    return RedirectResponse(url=authorization_url)

@router.get("/oauth2callback")
async def oauth2callback(request: Request):
    state = request.query_params.get('state')
    authorization_response = str(request.url)
    gdrive_loader.set_credentials(authorization_response, state)
    return RedirectResponse(url="/")

@router.get("/download_files/{folder_id}")
async def download_files(folder_id: str):
    try:
        downloaded_files = gdrive_loader.download_files(folder_id)
        if not downloaded_files:
            raise HTTPException(status_code=404, detail=f"No files found in folder ID: {folder_id}")
        return {"message": f"Files downloaded successfully!", "files": downloaded_files}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
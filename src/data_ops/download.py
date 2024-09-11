import os
import io
import pickle
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.errors import HttpError

router = APIRouter()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CLIENT_SECRETS_FILE = 'configs/credentials.json'
REDIRECT_URI = "http://localhost:8000/oauth2callback"
DOWNLOAD_FOLDER = 'data/raw_data'

def authenticate():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return authorization_url, state

@router.get("/authorize")
async def authorize():
    authorization_url, state = authenticate()
    response = RedirectResponse(url=authorization_url)
    return response

@router.get("/oauth2callback")
async def oauth2callback(request: Request):
    state = request.query_params.get('state')
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    return RedirectResponse(url="/")

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            raise Exception("Credentials are not valid, please authorize again.")
    service = build('drive', 'v3', credentials=creds)
    return service

@router.get("/download_files/{folder_id}")
async def download_files(folder_id: str):
    try:
        service = get_service()
        files = list_files_in_folder(service, folder_id)
        if not files:
            raise HTTPException(status_code=404, detail=f"No files found in folder ID: {folder_id}")
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        for file in files:
            if file['mimeType'] != 'application/vnd.google-apps.folder':
                download_file(service, file['id'], file['name'])
        return {"message": f"Files downloaded successfully to {DOWNLOAD_FOLDER}!"}
    except HttpError as error:
        raise HTTPException(status_code=error.resp.status, detail=str(error))

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents"
    try:
        results = service.files().list(q=query, pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])
        return items
    except HttpError as error:
        raise HTTPException(status_code=error.resp.status, detail=str(error))

def download_file(service, file_id, file_name, folder_path=DOWNLOAD_FOLDER):
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(folder_path, file_name)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading {file_name}: {int(status.progress() * 100)}%")
    print(f"{file_name} downloaded to {file_path}")

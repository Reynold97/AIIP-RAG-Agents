import os
import io
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CLIENT_SECRETS_FILE = 'app/configs/credentials.json'
REDIRECT_URI = "http://localhost:8000/gdrive/oauth2callback"
DOWNLOAD_FOLDER = 'data/raw_data'

def authenticate():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return authorization_url, state

def get_credentials_from_callback(authorization_response, state):
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials

def save_credentials(creds):
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

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
    return build('drive', 'v3', credentials=creds)

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents"
    try:
        results = service.files().list(q=query, pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()
        return results.get('files', [])
    except HttpError as error:
        raise error

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
    return file_path
import os
import io
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.errors import HttpError
import logging

# Allow OAuth2 insecure transport for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CLIENT_SECRETS_FILE = 'app/configs/credentials.json'
REDIRECT_URI = "http://localhost:8000/gdrive/oauth2callback"
DOWNLOAD_FOLDER = 'data/raw_data'

# MIME type mappings for Google Workspace files
GOOGLE_MIME_TYPES = {
    'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.spreadsheet': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.drawing': ('application/pdf', '.pdf'),
}

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
    query = f"'{folder_id}' in parents and (mimeType='application/pdf' or mimeType contains 'application/vnd.google-apps.')"
    try:
        results = service.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])
    except HttpError as error:
        logger.error(f"Error listing files: {str(error)}")
        raise

def download_file(service, file_id, file_name, mime_type, folder_path=DOWNLOAD_FOLDER):
    """Download or export a file from Google Drive"""
    try:
        # Create the download folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if mime_type in GOOGLE_MIME_TYPES:
            # Export Google Workspace files
            export_mime_type, extension = GOOGLE_MIME_TYPES[mime_type]
            request = service.files().export_media(
                fileId=file_id,
                mimeType=export_mime_type
            )
            # Ensure the filename has the correct extension
            if not file_name.endswith(extension):
                file_name = f"{file_name}{extension}"
        else:
            # Direct download for other files
            request = service.files().get_media(fileId=file_id)

        file_path = os.path.join(folder_path, file_name)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            logger.info(f"Downloading {file_name}: {int(status.progress() * 100)}%")

        logger.info(f"Downloaded {file_name} to {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error downloading file {file_name}: {str(e)}")
        raise

def download_files(service, folder_id):
    """Download all files from a folder"""
    try:
        files = list_files_in_folder(service, folder_id)
        if not files:
            return []

        downloaded_files = []
        for file in files:
            try:
                file_path = download_file(
                    service,
                    file['id'],
                    file['name'],
                    file['mimeType']
                )
                downloaded_files.append(file_path)
            except Exception as e:
                logger.error(f"Error downloading {file['name']}: {str(e)}")
                continue

        return downloaded_files

    except Exception as e:
        logger.error(f"Error downloading files from folder: {str(e)}")
        raise
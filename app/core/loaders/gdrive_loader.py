import os
from app.services import google_drive

class GDriveLoader:
    def __init__(self):
        self.service = None

    def authenticate(self):
        return google_drive.authenticate()

    def set_credentials(self, authorization_response, state):
        creds = google_drive.get_credentials_from_callback(authorization_response, state)
        google_drive.save_credentials(creds)

    def initialize_service(self):
        self.service = google_drive.get_service()

    def download_files(self, folder_id):
        if not self.service:
            self.initialize_service()

        files = google_drive.list_files_in_folder(self.service, folder_id)
        if not files:
            return []

        downloaded_files = []
        os.makedirs(google_drive.DOWNLOAD_FOLDER, exist_ok=True)
        for file in files:
            if file['mimeType'] != 'application/vnd.google-apps.folder':
                file_path = google_drive.download_file(self.service, file['id'], file['name'])
                downloaded_files.append(file_path)

        return downloaded_files
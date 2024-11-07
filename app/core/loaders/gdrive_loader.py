import os
from app.services import google_drive
import logging

logger = logging.getLogger(__name__)

class GDriveLoader:
    def __init__(self):
        self.service = None

    def authenticate(self):
        return google_drive.authenticate()

    def set_credentials(self, authorization_response, state):
        creds = google_drive.get_credentials_from_callback(authorization_response, state)
        google_drive.save_credentials(creds)

    def initialize_service(self):
        if not self.service:
            self.service = google_drive.get_service()

    def download_files(self, folder_id):
        """Download files from a Google Drive folder"""
        try:
            if not self.service:
                self.initialize_service()

            downloaded_files = google_drive.download_files(self.service, folder_id)
            
            if not downloaded_files:
                logger.warning(f"No files found in folder {folder_id}")
                return []

            # Return only the filenames for the UI
            return [os.path.basename(file_path) for file_path in downloaded_files]

        except Exception as e:
            logger.error(f"Error downloading files: {str(e)}")
            raise
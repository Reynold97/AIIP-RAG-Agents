import os
import shutil
from pathlib import Path
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

class FileManager:
    RAW_DATA_DIR = "data/raw_data"
    
    @classmethod
    def ensure_raw_data_dir(cls):
        """Ensure the raw data directory exists"""
        os.makedirs(cls.RAW_DATA_DIR, exist_ok=True)
    
    @classmethod
    def get_raw_data_files(cls) -> Set[str]:
        """Get list of files in raw data directory"""
        cls.ensure_raw_data_dir()
        return {f for f in os.listdir(cls.RAW_DATA_DIR) if f.lower().endswith('.pdf')}
    
    @classmethod
    def save_uploaded_file(cls, file) -> str:
        """Save an uploaded file to raw data directory"""
        try:
            cls.ensure_raw_data_dir()
            file_path = os.path.join(cls.RAW_DATA_DIR, file.name)
            
            # If file exists, add a number to the filename
            base_name, extension = os.path.splitext(file.name)
            counter = 1
            while os.path.exists(file_path):
                new_name = f"{base_name}_{counter}{extension}"
                file_path = os.path.join(cls.RAW_DATA_DIR, new_name)
                counter += 1
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(file.getvalue())
            
            logger.info(f"Successfully saved file to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {file.name}: {str(e)}")
            raise
    
    @classmethod
    def get_file_path(cls, filename: str) -> str:
        """Get full path for a file in raw data directory"""
        return os.path.join(cls.RAW_DATA_DIR, filename)
    
    @classmethod
    def is_valid_pdf(cls, file_path: str) -> bool:
        """Check if a file is a valid PDF"""
        return os.path.exists(file_path) and file_path.lower().endswith('.pdf')
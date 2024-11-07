import requests
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class APIClient:
    @staticmethod
    def make_request(
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True
    ) -> Dict[str, Any]:
        """Make a request to the API endpoint."""
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json,
                files=files
            )
            
            if raise_for_status:
                response.raise_for_status()
                
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

class ChromaDBClient:
    """Client for ChromaDB API operations"""
    
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
        
    def create_database(self) -> Dict[str, str]:
        """Initialize ChromaDB database"""
        return APIClient.make_request("POST", self.endpoints["create"])
    
    def delete_database(self) -> Dict[str, str]:
        """Delete ChromaDB database"""
        return APIClient.make_request("DELETE", self.endpoints["delete"])
    
    def create_collection(self, collection_name: str) -> Dict[str, str]:
        """Create a new collection"""
        url = f"{self.endpoints['create_collection']}/{collection_name}"
        return APIClient.make_request("POST", url)
    
    def delete_collection(self, collection_name: str) -> Dict[str, str]:
        """Delete a collection"""
        url = f"{self.endpoints['delete_collection']}/{collection_name}"
        return APIClient.make_request("DELETE", url)
    
    def list_collections(self) -> Dict[str, list]:
        """List all collections"""
        return APIClient.make_request("GET", self.endpoints["list_collections"])

class ChromaIndexClient:
    """Client for Chroma indexing operations"""
    
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
        
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, str]:
        """Add documents to collection"""
        url = f"{self.endpoints['add_documents']}/{collection_name}/add_documents"
        return APIClient.make_request("POST", url, json=documents)
    
    def search_documents(self, collection_name: str, query: str, k: int = 4) -> Dict[str, List]:
        """Search documents in collection"""
        url = f"{self.endpoints['search']}/{collection_name}/search"
        return APIClient.make_request("GET", url, params={"query": query, "k": k})
    
    def delete_document(self, collection_name: str, document_id: str) -> Dict[str, str]:
        """Delete document from collection"""
        url = f"{self.endpoints['delete_document']}/{collection_name}/documents/{document_id}"
        return APIClient.make_request("DELETE", url)
    
    def update_document(self, collection_name: str, document_id: str, document: Dict[str, Any]) -> Dict[str, str]:
        """Update document in collection"""
        url = f"{self.endpoints['update_document']}/{collection_name}/documents/{document_id}"
        return APIClient.make_request("PUT", url, json=document)
    
    def count_documents(self, collection_name: str) -> Dict[str, int]:
        """Get document count in collection"""
        url = f"{self.endpoints['count']}/{collection_name}/count"
        return APIClient.make_request("GET", url)
    
    def process_pdfs(self, collection_name: str, pdf_files: List[Path]) -> Dict[str, str]:
        """Process PDF files and add to collection"""
        url = f"{self.endpoints['process_pdfs']}/{collection_name}/process_pdfs"
        files = [("files", (f.name, open(f, "rb"), "application/pdf")) for f in pdf_files]
        return APIClient.make_request("POST", url, files=files)
    
    def process_folder(self, collection_name: str, folder_path: str) -> Dict[str, str]:
        """Process folder of PDFs and add to collection"""
        url = f"{self.endpoints['process_folder']}/{collection_name}/process_folder"
        return APIClient.make_request("POST", url, json={"folder_path": folder_path})

class GDriveClient:
    """Client for Google Drive operations"""
    
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
        
    def get_auth_url(self) -> str:
        """Get Google Drive authorization URL"""
        return self.endpoints["authorize"]
    
    def download_files(self, folder_id: str) -> Dict[str, Any]:
        """Download files from Google Drive folder"""
        url = f"{self.endpoints['download_files']}/{folder_id}"
        return APIClient.make_request("GET", url)
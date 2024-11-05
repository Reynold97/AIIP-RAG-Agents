import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class APIClient:
    @staticmethod
    def make_request(
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True
    ) -> Dict[str, Any]:
        """
        Make a request to the API endpoint.
        
        Args:
            method: HTTP method to use
            url: URL to make request to
            params: Query parameters
            json: JSON body
            raise_for_status: Whether to raise an exception for error status codes
            
        Returns:
            Response data as dictionary
        """
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json
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
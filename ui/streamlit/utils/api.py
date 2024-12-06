import json
import requests
from typing import Callable, Generator, Optional, Dict, Any, List, Union, Iterator
import logging
from pathlib import Path
import os
from contextlib import ExitStack, contextmanager

logger = logging.getLogger(__name__)

class APIClient:
    @staticmethod
    def make_request(
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True
    ) -> Dict[str, Any]:
        """Make a request to the API endpoint."""
        try:
            # Debug print
            logger.info(f"Making {method} request to {url}")
            if json:
                logger.info(f"Request body: {json}")

            response = requests.request(
                method=method,
                url=url,
                json=json,
                files=files
            )
            
            # Debug print response
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            if raise_for_status:
                response.raise_for_status()
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            raise

class ChromaDBClient:
    """Client for ChromaDB API operations"""
    
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
        
    def create_database(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize or reconfigure ChromaDB database"""
        return APIClient.make_request("POST", self.endpoints["create"], json=config)
    
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
        
    def list_embeddings(self) -> Dict[str, Dict[str, Any]]:
        """Get available embedding models"""
        return APIClient.make_request("GET", self.endpoints["list_embeddings"])

class ChromaIndexClient:
    """Client for Chroma indexing operations"""
    
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
        
    def process_pdfs(
        self, 
        collection_name: str, 
        file_paths: List[str],
        chunk_size: int = 10000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """Process PDF files and add to collection"""
        url = f"{self.endpoints['process_pdfs']}/{collection_name}/process_pdfs"
        
        # Use ExitStack to manage multiple file handles
        with ExitStack() as stack:
            files = []
            for file_path in file_paths:
                try:
                    abs_path = os.path.abspath(file_path)
                    if os.path.exists(abs_path) and abs_path.lower().endswith('.pdf'):
                        f = stack.enter_context(open(abs_path, 'rb'))
                        filename = os.path.basename(abs_path)
                        files.append(('files', (filename, f, 'application/pdf')))
                    else:
                        logger.warning(f"Skipping invalid file: {file_path}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    raise
            
            if not files:
                raise ValueError("No valid PDF files to process")
            
            # Add chunking parameters to request
            params = {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            }
            
            return APIClient.make_request("POST", url, files=files, params=params)
    
    def search_documents(
        self, 
        collection_name: str, 
        query: str,
        retriever_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List]:
        """Search documents in collection with optional retriever config"""
        url = f"{self.endpoints['search']}/{collection_name}/search"
        
        # Default configuration if none provided
        if retriever_config is None:
            retriever_config = {
                "collection_name": collection_name,  # Added this field
                "search_type": "similarity",
                "k": 100 if not query else 4,
                "search_parameters": {}
            }
        else:
            # Ensure collection_name is in the config
            retriever_config["collection_name"] = collection_name

        try:
            # Prepare request body
            request_body = {
                "query": str(query).strip(),
                "retriever_config": retriever_config
            }
            
            # Debug print
            logger.info(f"Making request to {url}")
            logger.info(f"Request body: {request_body}")

            # Send request
            response = APIClient.make_request(
                method="POST",
                url=url,
                json=request_body
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in search documents: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response content: {e.response.text}")
            raise
        
    def process_folder(
        self, 
        collection_name: str, 
        folder_path: str,
        chunk_size: int = 10000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """Process folder of PDFs with chunking parameters"""
        url = f"{self.endpoints['process_folder']}/{collection_name}/process_folder"
        params = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
        return APIClient.make_request(
            "POST", 
            url, 
            json={"folder_path": folder_path},
            params=params
        )
    
    def count_documents(self, collection_name: str) -> Dict[str, int]:
        """Get document count in collection"""
        url = f"{self.endpoints['count']}/{collection_name}/count"
        return APIClient.make_request("GET", url)
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, str]:
        """Add documents to collection"""
        url = f"{self.endpoints['add_documents']}/{collection_name}/add_documents"
        return APIClient.make_request("POST", url, json=documents)
    
    def delete_document(self, collection_name: str, document_id: str) -> Dict[str, str]:
        """Delete document from collection"""
        url = f"{self.endpoints['delete_document']}/{collection_name}/documents/{document_id}"
        return APIClient.make_request("DELETE", url)
    
    def update_document(self, collection_name: str, document_id: str, document: Dict[str, Any]) -> Dict[str, str]:
        """Update document in collection"""
        url = f"{self.endpoints['update_document']}/{collection_name}/documents/{document_id}"
        return APIClient.make_request("PUT", url, json=document)

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

class AgentResponse:
    """Wrapper class for agent responses to handle both streaming and non-streaming cases"""
    def __init__(self, data: Union[Dict[str, Any], Callable[[], Iterator[Dict[str, Any]]], Iterator[Dict[str, Any]]], is_streaming: bool):
        self.data = data
        self.is_streaming = is_streaming
        self._iterator = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from response data"""
        if self.is_streaming:
            raise ValueError("Cannot use get() on streaming response. Use iterate() instead.")
        return self.data.get(key, default)
    
    def iterate(self) -> Iterator[Dict[str, Any]]:
        """Iterate over streaming response"""
        if not self.is_streaming:
            raise ValueError("Cannot iterate non-streaming response. Use get() instead.")
        
        # If data is a generator function, call it once
        if self._iterator is None:
            if callable(self.data):
                self._iterator = self.data()
            else:
                self._iterator = self.data
                
        return self._iterator

class AgentClient:
    """Client for RAG Agent operations"""
    
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
    
    @contextmanager
    def _handle_request_errors(self, operation: str):
        """Context manager for handling request errors"""
        try:
            yield
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in {operation}: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text}")
            raise RuntimeError(f"Error in {operation}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {operation}: {str(e)}")
            raise
    
    def _parse_sse_line(self, line: bytes) -> Optional[Dict[str, Any]]:
        """Parse a single SSE line"""
        try:
            if not line:
                return None
            line_str = line.decode('utf-8')
            if not line_str.startswith('data: '):
                return None
            return json.loads(line_str[6:])
        except Exception as e:
            logger.error(f"Error parsing SSE line: {str(e)}")
            return {"error": str(e)}
    
    def query_agent(
        self,
        agent_type: str,
        question: str,
        config: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AgentResponse:
        """Query the RAG agent"""
        url = f"{self.endpoints['agent']}/{agent_type}"
        body = {
            "question": question,
            "stream": stream,
            "config": config
        }
        
        logger.debug(f"Sending request to {url} with body: {body}")
        
        with self._handle_request_errors("query_agent"):
            if stream:
                # Return the generator function instead of calling it
                def stream_generator():
                    with requests.post(url, json=body, stream=True) as response:
                        response.raise_for_status()
                        for line in response.iter_lines():
                            if parsed := self._parse_sse_line(line):
                                yield parsed
                
                # Pass the generator function, not the generator object
                return AgentResponse(stream_generator, is_streaming=True)
            else:
                response = requests.post(url, json=body)
                response.raise_for_status()
                return AgentResponse(response.json(), is_streaming=False)
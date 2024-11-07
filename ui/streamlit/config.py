# API endpoint configurations
API_BASE_URL = "http://localhost:8000"

# Database operations endpoints
DB_ENDPOINTS = {
    "create": f"{API_BASE_URL}/chromadb/create",
    "delete": f"{API_BASE_URL}/chromadb/delete",
    "create_collection": f"{API_BASE_URL}/chromadb/collections",  # /{collection_name}
    "delete_collection": f"{API_BASE_URL}/chromadb/collections",  # /{collection_name}
    "list_collections": f"{API_BASE_URL}/chromadb/collections",
}

# Index operations endpoints
INDEX_ENDPOINTS = {
    "add_documents": f"{API_BASE_URL}/chroma",  # /{collection_name}/add_documents
    "search": f"{API_BASE_URL}/chroma",  # /{collection_name}/search
    "delete_document": f"{API_BASE_URL}/chroma",  # /{collection_name}/documents/{document_id}
    "update_document": f"{API_BASE_URL}/chroma",  # /{collection_name}/documents/{document_id}
    "count": f"{API_BASE_URL}/chroma",  # /{collection_name}/count
    "process_pdfs": f"{API_BASE_URL}/chroma",  # /{collection_name}/process_pdfs
    "process_folder": f"{API_BASE_URL}/chroma",  # /{collection_name}/process_folder
}

# Google Drive endpoints
GDRIVE_ENDPOINTS = {
    "authorize": f"{API_BASE_URL}/gdrive/authorize",
    "oauth2callback": f"{API_BASE_URL}/gdrive/oauth2callback",
    "download_files": f"{API_BASE_URL}/gdrive/download_files",  # /{folder_id}
}

# Styling configurations
STYLES = {
    "success_color": "#0FBA81",
    "error_color": "#FF4B4B",
    "warning_color": "#FFA726",
    "info_color": "#2196F3",
}
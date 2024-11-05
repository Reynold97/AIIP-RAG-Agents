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

# Styling configurations
STYLES = {
    "success_color": "#0FBA81",
    "error_color": "#FF4B4B",
    "warning_color": "#FFA726",
    "info_color": "#2196F3",
}
from typing import Any, Dict, List
import streamlit as st
import sys
from pathlib import Path
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from utils.api import ChromaIndexClient, GDriveClient
from utils.file_utils import FileManager
from components.status import show_status_message, show_operation_status
from config import INDEX_ENDPOINTS, GDRIVE_ENDPOINTS

def init_page():
    st.set_page_config(
        page_title="Index Operations",
        page_icon="📑",
        layout="wide"
    )
    st.title("Document Processing & Index Operations 📑")
    
    # Check for auth callback
    if st.query_params.get("auth_success"):
        st.session_state.drive_authorized = True
        st.query_params.clear()
    
    # Initialize API clients
    index_client = ChromaIndexClient(INDEX_ENDPOINTS)
    gdrive_client = GDriveClient(GDRIVE_ENDPOINTS)
    
    return index_client, gdrive_client

def check_drive_auth():
    """Check if already authorized with Google Drive"""
    return os.path.exists('token.pickle')

def render_gdrive_section(gdrive_client: GDriveClient):
    """Render Google Drive integration section"""
    st.header("Google Drive Integration")
    
    # Initialize session state for drive authorization
    if "drive_authorized" not in st.session_state:
        st.session_state.drive_authorized = check_drive_auth()
    
    # Step 1: Authorization
    if not st.session_state.drive_authorized:
        st.write("🔐 Connect to Google Drive to access your files")
        if st.button("Connect to Google Drive", type="primary"):
            try:
                auth_url = gdrive_client.get_auth_url()
                st.markdown(
                    """
                    1. Click the link below to authorize access to Google Drive
                    2. After authorization, you'll be redirected back automatically
                    """
                )
                st.markdown(f"[Click here to authorize]({auth_url})")
            except Exception as e:
                show_status_message(f"Error connecting to Google Drive: {str(e)}", type="error")
        return
    
    # Step 2: Folder Selection (only shown after authorization)
    st.success("✅ Connected to Google Drive")
    
    with st.form("folder_form"):
        folder_id = st.text_input(
            "Folder ID",
            help="Enter the Google Drive folder ID containing your PDFs"
        )
        submit_button = st.form_submit_button("Download Files", type="primary")
    
    # Process download outside the form to maintain success message
    if submit_button and folder_id:
        try:
            with st.spinner("Downloading files from Drive..."):
                response = gdrive_client.download_files(folder_id)
                if response and isinstance(response, dict) and response.get("files"):
                    downloaded_files = response["files"]
                    st.session_state.downloaded_files = downloaded_files
                    file_count = len(downloaded_files)
                    logger.info(f"Downloaded files: {downloaded_files}")
                    
                    # Create success message with file names using markdown
                    success_msg = [
                        f"✨ Successfully downloaded {file_count} document{'s' if file_count > 1 else ''}:",
                        "",  # Empty line for spacing
                        *[f"* {file}" for file in downloaded_files]
                    ]
                    st.success("\n".join(success_msg))
                else:
                    st.info("No files found in the specified folder")
        except Exception as e:
            show_status_message(f"Error downloading files: {str(e)}", type="error")

def render_local_upload():
    """Render local file upload section"""
    st.header("Local File Upload")
    
    # Initialize session state
    if "upload_status" not in st.session_state:
        st.session_state.upload_status = {"completed": False, "files": set()}
    
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if uploaded_files:
        # Get filenames of newly uploaded files
        current_files = {f.name for f in uploaded_files}
        new_files = current_files - st.session_state.upload_status["files"]
        
        if new_files:  # Only process new files
            with st.spinner("Copying files to raw data directory..."):
                uploaded_count = 0
                for file in uploaded_files:
                    if file.name in new_files:
                        try:
                            FileManager.save_uploaded_file(file)
                            uploaded_count += 1
                            st.session_state.upload_status["files"].add(file.name)
                        except Exception as e:
                            show_status_message(f"Error saving file {file.name}: {str(e)}", type="error")
                            continue
                
                if uploaded_count > 0:
                    show_status_message(f"Successfully uploaded {uploaded_count} files", type="success")
    
    # Clear status when no files are selected
    elif st.session_state.upload_status["files"]:
        st.session_state.upload_status = {"completed": False, "files": set()}
        
def render_available_documents():
    """Render available documents section"""
    st.subheader("Available Documents")  # Changed from header to subheader
    
    # Get files from raw data directory
    available_files = FileManager.get_raw_data_files()
    
    if not available_files:
        st.info("No documents available. Upload files or download from Google Drive.")
        return []
    
    st.write(f"Found {len(available_files)} documents in raw data directory:")
    
    # Create checkboxes for file selection with two columns
    col1, col2 = st.columns(2)
    
    selected_files = []
    for idx, file in enumerate(sorted(available_files)):
        # Alternate between columns
        with col1 if idx % 2 == 0 else col2:
            if st.checkbox(f"📄 {file}", key=f"file_{file}"):
                file_path = FileManager.get_file_path(file)
                if FileManager.is_valid_pdf(file_path):
                    selected_files.append(file_path)
                else:
                    st.warning(f"Invalid or missing file: {file}")
    
    return selected_files

def render_document_processing(client: ChromaIndexClient):
    """Render document processing section with chunking options"""
    st.header("Document Processing")
    
    # Collection selection for processing
    collection_name = st.text_input("Target Collection Name")
    if not collection_name:
        st.warning("Please enter a collection name to process documents")
        return
        
    # Show current collection documents
    st.subheader(f"Current Documents in {collection_name}")
    render_collection_documents(client, collection_name)
    
    # Process new documents
    st.subheader("Process New Documents")
    
    # Chunking parameters
    with st.expander("Chunking Configuration", expanded=False):
        chunk_size = st.slider(
            "Chunk Size",
            min_value=100,
            max_value=20000,
            value=10000,
            step=1000,
            help="Size of document chunks. Larger values mean longer but fewer chunks"
        )
        
        chunk_overlap = st.slider(
            "Chunk Overlap",
            min_value=0,
            max_value=2000,
            value=200,
            step=100,
            help="Number of characters to overlap between chunks. Helps maintain context"
        )
        
        st.info("""
        Chunk size recommendations:
        - 10000: Good for general purpose use
        - 4000: Better for precise retrievals
        - 1000 and less: Best for very specific queries
        
        Overlap recommendations:
        - 200: Standard overlap
        - 500: More context preservation
        - 1000: Maximum context preservation
        """)
    
    selected_files = render_available_documents()
    
    if selected_files:
        num_selected = len(selected_files)
        container = st.container()
        with container:
            st.write(f"Selected {num_selected} document{'s' if num_selected > 1 else ''} for processing")
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Process Files", type="primary"):
                    try:
                        with st.spinner(f"Processing {num_selected} files..."):
                            logger.info(f"Starting to process {num_selected} files for collection {collection_name}")
                            response = client.process_pdfs(
                                collection_name,
                                selected_files,
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap
                            )
                            if response.get("message"):
                                show_operation_status(response["message"])
                                st.success(f"Chunking config used: Size={chunk_size}, Overlap={chunk_overlap}")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        logger.error(f"Error processing files: {str(e)}", exc_info=True)
                        show_status_message(f"Error processing files: {str(e)}", type="error")
    else:
        st.info("Select documents to process from the list above")

def render_collection_documents(client: ChromaIndexClient, collection_name: str):
    """Render documents in collection with search configuration"""
    try:
        count = client.count_documents(collection_name)
        total_docs = count.get("count", 0)
        st.metric("Total Chunks in Collection", total_docs)
        
        if total_docs > 0:
            view_tab, search_tab = st.tabs(["📚 Collection Overview", "🔍 Search Documents"])
            
            with view_tab:
                try:
                    with st.spinner("Loading documents..."):
                        # Overview request
                        overview_config = {
                            "search_type": "similarity",
                            "k": 100,
                            "search_parameters": {}
                        }
                        results = client.search_documents(
                            collection_name=collection_name,
                            query="",  # Empty query for overview
                            retriever_config=overview_config
                        )
                        if results.get("results"):
                            render_document_results(results["results"], context="overview")
                        else:
                            st.info("No documents to display")
                except Exception as e:
                    st.error(f"Error loading document overview: {str(e)}")
                    logger.error(f"Document overview error: {str(e)}", exc_info=True)
            
            with search_tab:
                # Search configuration
                with st.expander("Search Configuration", expanded=False):
                    search_type = st.selectbox(
                        "Search Type",
                        options=["similarity", "mmr", "similarity_score_threshold"],
                        help="""
                        - similarity: Standard similarity search
                        - mmr: Maximal Marginal Relevance for diverse results
                        - similarity_score_threshold: Filter by minimum similarity
                        """
                    )
                    
                    k = st.slider(
                        "Number of results", 
                        min_value=1, 
                        max_value=20, 
                        value=4,
                        help="Number of documents to return"
                    )
                    
                    # Additional parameters based on search type
                    search_parameters = {}
                    if search_type == "mmr":
                        search_parameters["fetch_k"] = st.slider(
                            "Fetch K (MMR)",
                            min_value=k,
                            max_value=50,
                            value=20,
                            help="Number of documents to fetch before reranking"
                        )
                        search_parameters["lambda_mult"] = st.slider(
                            "Lambda (Diversity)",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.5,
                            help="0 = maximum diversity, 1 = maximum relevance"
                        )
                    elif search_type == "similarity_score_threshold":
                        search_parameters["score_threshold"] = st.slider(
                            "Score Threshold",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.8,
                            help="Minimum similarity score (0-1) for results"
                        )
                
                # Search interface
                query = st.text_input(
                    "Search Query",
                    key="search_input",
                    help="Enter your search query"
                )
                
                if query:
                    try:
                        with st.spinner("Searching..."):
                            # Clean and prepare the query
                            query_str = str(query).strip()
                            
                            # Construct retriever config
                            retriever_config = {
                                "search_type": search_type,
                                "k": k,
                                "search_parameters": search_parameters
                            }
                            
                            # Debug info
                            logger.debug(f"Search params - Query: '{query_str}', Config: {retriever_config}")
                            
                            # Make the search request
                            results = client.search_documents(
                                collection_name=collection_name,
                                query=query_str,
                                retriever_config=retriever_config
                            )
                            
                            if results.get("results"):
                                # Show search configuration used
                                st.success(f"""
                                    Search performed with:
                                    - Query: "{query_str}"
                                    - Type: {search_type}
                                    - K: {k}
                                    {f'- Additional parameters: {search_parameters}' if search_parameters else ''}
                                """)
                                render_document_results(results["results"], context="search")
                            else:
                                st.info(f"No results found for query: '{query_str}'")
                    except Exception as e:
                        logger.error(f"Search error: {str(e)}", exc_info=True)
                        st.error(f"Error performing search: {str(e)}")
                        # Additional debug info
                        logger.debug(f"Failed request details - Query: '{query}', Type: {type(query)}")
            
        else:
            st.info("Collection is empty. Process some documents to see them here.")
            
    except Exception as e:
        logger.error(f"Error fetching collection documents: {str(e)}", exc_info=True)
        show_status_message(f"Error fetching collection documents: {str(e)}", type="error")

def render_document_results(results: List[Dict[str, Any]], context: str = "overview"):
    """Helper function to render document results
    
    Args:
        results: List of document results to render
        context: String indicating the context ("overview" or "search") to create unique keys
    """
    # Group chunks by source file
    docs_by_file = {}
    for doc in results:
        source_file = doc.get("metadata", {}).get("source_file", "Unknown Source")
        if source_file not in docs_by_file:
            docs_by_file[source_file] = []
        docs_by_file[source_file].append(doc)
    
    # Display documents grouped by file
    for file_name, chunks in docs_by_file.items():
        with st.expander(f"📄 {file_name} ({len(chunks)} chunks)"):
            st.write(f"**Source File:** {file_name}")
            for idx, chunk in enumerate(chunks, 1):
                st.markdown("---")
                st.write(f"**Chunk {idx}** (Page: {chunk.get('metadata', {}).get('page_number', 'Unknown')})")
                
                # Create two columns: one for preview, one for "Show full content" button
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(chunk.get('page_content', '')[:200] + "...")
                with col2:
                    # Use context in key to make it unique
                    button_key = f"{context}_show_content_{file_name}_{idx}"
                    toggle_key = f"{context}_toggle_{file_name}_{idx}"
                    
                    if toggle_key not in st.session_state:
                        st.session_state[toggle_key] = False
                        
                    if st.button("Show Full", key=button_key):
                        st.session_state[toggle_key] = not st.session_state[toggle_key]
                
                # Show full content if button was clicked
                if st.session_state[toggle_key]:
                    st.text(chunk.get('page_content', ''))

def main():
    index_client, gdrive_client = init_page()
    
    # Main sections
    render_gdrive_section(gdrive_client)
    st.divider()
    render_local_upload()
    st.divider()
    render_document_processing(index_client)

if __name__ == "__main__":
    main()
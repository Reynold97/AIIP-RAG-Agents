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
        auth_col1, auth_col2 = st.columns([2, 1])
        with auth_col1:
            st.write("🔐 Connect to Google Drive to access your files")
        with auth_col2:
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
        
        if submit_button and folder_id:
            try:
                with st.spinner("Downloading files from Drive..."):
                    response = gdrive_client.download_files(folder_id)
                    if response.get("files"):
                        st.session_state.downloaded_files = response["files"]
                        show_operation_status("File download")
                        st.rerun()
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

def render_collection_documents(client: ChromaIndexClient, collection_name: str):
    """Render documents in collection"""
    try:
        # Get document count
        count = client.count_documents(collection_name)
        total_docs = count.get("count", 0)
        st.metric("Total Chunks in Collection", total_docs)
        
        # Search functionality for viewing documents
        st.subheader("Indexed Documents")
        if total_docs > 0:
            # Create tabs for different views
            view_tab, search_tab = st.tabs(["📚 Document Overview", "🔍 Search Documents"])
            
            with view_tab:
                # Get all documents (limited to recent ones to avoid overwhelming)
                results = client.search_documents(collection_name, "", min(total_docs, 100))
                if results.get("results"):
                    # Group chunks by source file
                    docs_by_file = {}
                    for doc in results["results"]:
                        source_file = doc.get("metadata", {}).get("source_file", "Unknown Source")
                        if source_file not in docs_by_file:
                            docs_by_file[source_file] = []
                        docs_by_file[source_file].append(doc)
                    
                    # Display documents grouped by file
                    for file_name, chunks in docs_by_file.items():
                        with st.expander(f"📄 {file_name} ({len(chunks)} chunks)"):
                            # Display file info
                            st.write(f"**Source File:** {file_name}")
                            # Show chunks in a scrollable container
                            for idx, chunk in enumerate(chunks, 1):
                                st.markdown("---")
                                st.write(f"**Chunk {idx}** (Page: {chunk.get('metadata', {}).get('page_number', 'Unknown')})")
                                # Create two columns: one for preview, one for "Show full content" button
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.text(chunk.get('page_content', '')[:200] + "...")
                                with col2:
                                    # Use a button to toggle full content visibility
                                    button_key = f"show_content_{file_name}_{idx}"
                                    if button_key not in st.session_state:
                                        st.session_state[button_key] = False
                                    if st.button("Show Full", key=f"btn_{file_name}_{idx}"):
                                        st.session_state[button_key] = not st.session_state[button_key]
                                
                                # Show full content if button was clicked
                                if st.session_state[button_key]:
                                    st.text(chunk.get('page_content', ''))
            
            with search_tab:
                # Initialize session state for search
                if 'search_query' not in st.session_state:
                    st.session_state.search_query = ''
                if 'search_results' not in st.session_state:
                    st.session_state.search_results = None
                
                # Search interface
                query = st.text_input("Search Query", key="search_input")
                k = st.slider("Number of results", min_value=1, max_value=10, value=4)
                
                # Only perform search if query changes or button is clicked
                if st.button("Search", disabled=not query) or (query != st.session_state.search_query and query):
                    try:
                        with st.spinner("Searching..."):
                            st.session_state.search_query = query
                            results = client.search_documents(collection_name, query, k)
                            st.session_state.search_results = results.get("results", [])
                    except Exception as e:
                        show_status_message(f"Error searching documents: {str(e)}", type="error")
                
                # Display results from session state
                if st.session_state.search_results:
                    for idx, doc in enumerate(st.session_state.search_results, 1):
                        st.markdown("---")
                        st.write(f"**Result {idx}**")
                        metadata = doc.get("metadata", {})
                        st.write(f"**Source:** {metadata.get('source_file', 'Unknown')}")
                        st.write(f"**Page:** {metadata.get('page_number', 'Unknown')}")
                        # Create two columns: one for preview, one for "Show full content" button
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.text(doc.get('page_content', '')[:200] + "...")
                        with col2:
                            # Use a button to toggle full content visibility
                            button_key = f"show_search_{query}_{idx}"
                            if button_key not in st.session_state:
                                st.session_state[button_key] = False
                            if st.button("Show Full", key=f"btn_search_{query}_{idx}"):
                                st.session_state[button_key] = not st.session_state[button_key]
                        
                        # Show full content if button was clicked
                        if st.session_state[button_key]:
                            st.text(doc.get('page_content', ''))
                elif st.session_state.search_query:
                    st.info("No results found")
                    
        else:
            st.info("Collection is empty. Process some documents to see them here.")
            
    except Exception as e:
        logger.error(f"Error fetching collection documents: {str(e)}", exc_info=True)
        show_status_message(f"Error fetching collection documents: {str(e)}", type="error")

def render_document_processing(client: ChromaIndexClient):
    """Render document processing section"""
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
    selected_files = render_available_documents()
    
    if selected_files:
        num_selected = len(selected_files)
        container = st.container()
        with container:
            st.write(f"Selected {num_selected} document{'s' if num_selected > 1 else ''} for processing")
            col1, col2 = st.columns([1, 4])  # Use columns to align button to the left
            with col1:
                if st.button("Process Files", type="primary"):
                    try:
                        with st.spinner(f"Processing {num_selected} files..."):
                            logger.info(f"Starting to process {num_selected} files for collection {collection_name}")
                            response = client.process_pdfs(collection_name, selected_files)
                            if response.get("message"):
                                show_operation_status(response["message"])
                            else:
                                show_operation_status("File processing")
                            logger.info("File processing completed successfully")
                            time.sleep(1)  # Small delay to ensure UI updates
                            st.rerun()  # Refresh to show updated collection documents
                    except ValueError as e:
                        error_msg = str(e)
                        logger.error(f"Validation error: {error_msg}")
                        show_status_message(error_msg, type="error")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Error processing files: {error_msg}", exc_info=True)
                        show_status_message(f"Error processing files: {error_msg}", type="error")
    else:
        st.info("Select documents to process from the list above")

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
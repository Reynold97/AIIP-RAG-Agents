import streamlit as st
import sys
from pathlib import Path
import time

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from utils.api import ChromaIndexClient, GDriveClient
from components.status import show_status_message, show_operation_status
from config import INDEX_ENDPOINTS, GDRIVE_ENDPOINTS

def init_page():
    st.set_page_config(
        page_title="Index Operations",
        page_icon="📑",
        layout="wide"
    )
    st.title("Document Processing & Index Operations 📑")
    
    # Initialize clients
    index_client = ChromaIndexClient(INDEX_ENDPOINTS)
    gdrive_client = GDriveClient(GDRIVE_ENDPOINTS)
    
    return index_client, gdrive_client

def render_collection_selector():
    """Render collection selection dropdown"""
    st.sidebar.header("Collection Selection")
    collection_name = st.sidebar.text_input("Collection Name")
    
    if not collection_name:
        st.warning("Please select a collection to proceed")
        st.stop()
        
    return collection_name

def render_gdrive_section(gdrive_client: GDriveClient):
    """Render Google Drive integration section"""
    st.header("Google Drive Integration")
    
    with st.expander("Download from Google Drive", expanded=False):
        folder_id = st.text_input(
            "Folder ID",
            help="Enter the Google Drive folder ID containing PDFs"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Connect to Google Drive", type="primary", disabled=not folder_id):
                try:
                    auth_url = gdrive_client.get_auth_url()
                    st.markdown(f"[Click here to authorize]({auth_url})")
                except Exception as e:
                    show_status_message(f"Error connecting to Google Drive: {str(e)}", type="error")
                    
        with col2:
            if st.button("Download Files", disabled=not folder_id):
                try:
                    with st.spinner("Downloading files..."):
                        response = gdrive_client.download_files(folder_id)
                        st.session_state.downloaded_files = response.get("files", [])
                        show_operation_status("File download")
                        st.experimental_rerun()
                except Exception as e:
                    show_status_message(f"Error downloading files: {str(e)}", type="error")

def render_local_upload():
    """Render local file upload section"""
    st.header("Local File Upload")
    
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = [f.name for f in uploaded_files]
        show_status_message(f"Uploaded {len(uploaded_files)} files", type="success")

def render_document_processing(client: ChromaIndexClient, collection_name: str):
    """Render document processing section"""
    st.header("Document Processing")
    
    # Show available files
    st.subheader("Available Files")
    files_to_process = []
    
    # Add downloaded files
    if "downloaded_files" in st.session_state:
        st.write("Files from Google Drive:")
        for file in st.session_state.downloaded_files:
            if st.checkbox(f"📄 {file}", key=f"gdrive_{file}"):
                files_to_process.append(Path(file))
                
    # Add uploaded files
    if "uploaded_files" in st.session_state:
        st.write("Uploaded files:")
        for file in st.session_state.uploaded_files:
            if st.checkbox(f"📄 {file}", key=f"upload_{file}"):
                files_to_process.append(Path(file))
    
    # Process files
    if files_to_process:
        if st.button("Process Selected Files", type="primary"):
            try:
                with st.spinner("Processing files..."):
                    response = client.process_pdfs(collection_name, files_to_process)
                    show_operation_status("File processing")
            except Exception as e:
                show_status_message(f"Error processing files: {str(e)}", type="error")
    else:
        st.info("No files selected for processing")

def render_index_operations(client: ChromaIndexClient, collection_name: str):
    """Render index operations section"""
    st.header("Index Operations")
    
    # Document count
    try:
        count = client.count_documents(collection_name)
        st.metric("Documents in Collection", count.get("count", 0))
    except Exception as e:
        show_status_message(f"Error getting document count: {str(e)}", type="error")
    
    # Search functionality
    st.subheader("Search Documents")
    query = st.text_input("Search Query")
    k = st.slider("Number of results", min_value=1, max_value=10, value=4)
    
    if st.button("Search", disabled=not query):
        try:
            with st.spinner("Searching..."):
                results = client.search_documents(collection_name, query, k)
                
                if results.get("results"):
                    for idx, doc in enumerate(results["results"], 1):
                        with st.expander(f"Result {idx}"):
                            st.json(doc)
                else:
                    st.info("No results found")
        except Exception as e:
            show_status_message(f"Error searching documents: {str(e)}", type="error")

def main():
    index_client, gdrive_client = init_page()
    
    # Get collection name
    collection_name = render_collection_selector()
    
    # Main sections
    render_gdrive_section(gdrive_client)
    st.divider()
    render_local_upload()
    st.divider()
    render_document_processing(index_client, collection_name)
    st.divider()
    render_index_operations(index_client, collection_name)

if __name__ == "__main__":
    main()
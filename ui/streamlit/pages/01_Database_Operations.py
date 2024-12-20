import streamlit as st
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))

from utils.api import ChromaDBClient
from components.status import show_status_message, show_operation_status
from config import DB_ENDPOINTS

def init_page():
    st.set_page_config(
        page_title="Database Operations",
        page_icon="🗄️",
        layout="wide"
    )
    st.title("ChromaDB Operations 🗄️")
    
    # Initialize API client
    return ChromaDBClient(DB_ENDPOINTS)

def render_database_section(client: ChromaDBClient):
    """Render database initialization section"""
    st.header("Database Management")
    
    # Get available embedding models
    try:
        embeddings_response = client.list_embeddings()
        available_embeddings = embeddings_response.get("embeddings", {})
    except Exception as e:
        show_status_message(f"Error fetching embedding models: {str(e)}", type="error")
        available_embeddings = {}

    # Database configuration form
    with st.expander("Configure Database", expanded=False):
        embedding_name = st.selectbox(
            "Embedding Model",
            options=list(available_embeddings.keys()),
            help="Select the embedding model to use"
        )
        
        space_type = st.selectbox(
            "Vector Space",
            options=["cosine", "l2", "ip"],
            help="Select the vector space type for similarity calculations"
        )
        
        if st.button("Apply Configuration", type="primary"):
            try:
                config = {
                    "database_type": "ChromaDB",
                    "collection_name": "default_collection",
                    "embedding": available_embeddings[embedding_name],
                    "parameters": {
                        "collection_metadata": {"hnsw:space": space_type}
                    }
                }
                response = client.create_database(config)
                show_operation_status("Database configuration")
            except Exception as e:
                show_status_message(f"Error configuring database: {str(e)}", type="error")

def render_collections_section(client: ChromaDBClient):
    """Render collections management section"""
    st.header("Collections Management")
    
    # Create collection
    with st.expander("Create New Collection", expanded=False):
        col_name = st.text_input("Collection Name")
        if st.button("Create Collection", disabled=not col_name):
            try:
                response = client.create_collection(col_name)
                show_operation_status("Collection creation")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                show_status_message(f"Error creating collection: {str(e)}", type="error")
    
    # List and manage collections
    st.subheader("Existing Collections")
    try:
        response = client.list_collections()
        collections = response.get("collections", [])
        
        if not collections:
            st.info("No collections found. Create one above! 👆")
        else:
            for col in collections:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📁 {col}")
                with col2:
                    if st.button("Delete", key=f"del_{col}", type="secondary"):
                        try:
                            if st.session_state.get(f"confirm_delete_{col}"):
                                response = client.delete_collection(col)
                                show_operation_status("Collection deletion")
                                st.session_state[f"confirm_delete_{col}"] = False
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_{col}"] = True
                                show_status_message(
                                    f"⚠️ Click again to confirm deletion of collection '{col}'",
                                    type="warning"
                                )
                        except Exception as e:
                            show_status_message(
                                f"Error deleting collection: {str(e)}",
                                type="error"
                            )
                            st.session_state[f"confirm_delete_{col}"] = False
    except Exception as e:
        show_status_message(f"Error listing collections: {str(e)}", type="error")

def main():
    client = init_page()
    
    # Render main sections
    render_database_section(client)
    st.divider()
    render_collections_section(client)

if __name__ == "__main__":
    main()
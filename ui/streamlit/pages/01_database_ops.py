import streamlit as st
import sys
from pathlib import Path
import time

# Add the parent directory to sys.path
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
    
    if st.button("Initialize Database", type="primary"):
        try:
            response = client.create_database()
            show_operation_status("Database initialization")
        except Exception as e:
            show_status_message(f"Error initializing database: {str(e)}", type="error")

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
                time.sleep(1)  # Small delay to ensure UI update
                st.rerun()  # Updated from experimental_rerun()
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
                                time.sleep(1)  # Small delay to ensure UI update
                                st.rerun()  # Updated from experimental_rerun()
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
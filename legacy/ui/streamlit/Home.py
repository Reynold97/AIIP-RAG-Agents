import streamlit as st

st.set_page_config(
    page_title="AIIP RAG Agents",
    page_icon="🤖",
    layout="wide"
)

st.title("Welcome to AIIP RAG Agents! 🤖")

st.markdown("""
### Navigate using the sidebar to:
1. 🗄️ **Database Operations**: Manage ChromaDB databases and collections
2. 📑 **Index Operations**: Process and index documents
3. 💬 **Agent Chat**: Interact with RAG agents

Choose an option from the sidebar to get started!
""")


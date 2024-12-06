from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.api import AgentResponse
import streamlit as st
import sys
from pathlib import Path
import time
import logging
from typing import Dict, Any, Generator, Optional
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.api import ChromaDBClient, AgentClient
from components.status import show_status_message
from config import DB_ENDPOINTS, AGENT_ENDPOINTS

class ChatUI:
    def __init__(self):
        """Initialize chat UI with API clients and session state"""
        self.db_client = ChromaDBClient(DB_ENDPOINTS)
        self.agent_client = AgentClient(AGENT_ENDPOINTS)
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_collection" not in st.session_state:
            st.session_state.current_collection = None
        if "agent_config" not in st.session_state:
            st.session_state.agent_config = None
        if "streaming_enabled" not in st.session_state:
            st.session_state.streaming_enabled = True
            
    def _format_docs(self, docs: list) -> str:
        """Format retrieved documents for display"""
        formatted = []
        for doc in docs:
            source = doc.get("metadata", {}).get("source_file", "Unknown")
            page = doc.get("metadata", {}).get("page_number", "Unknown")
            formatted.append(f"**Source:** {source} (Page {page})\n{doc.get('page_content', '')}\n")
        return "\n---\n".join(formatted)

    def render_sidebar(self):
        """Render sidebar with agent configuration options"""
        with st.sidebar:
            st.header("Agent Configuration")
            
            # Collection selection
            try:
                collections = self.db_client.list_collections().get("collections", [])
                if not collections:
                    st.warning("No collections available. Please create one first.")
                    return False
                
                selected_collection = st.selectbox(
                    "Select Collection",
                    options=collections,
                    index=collections.index(st.session_state.current_collection) if st.session_state.current_collection in collections else 0
                )
                st.session_state.current_collection = selected_collection
                
                # Agent type selection
                agent_type = st.radio(
                    "Select Agent Type",
                    options=["Simple RAG", "Complex RAG"],
                    help="""
                    Simple RAG: Basic retrieval and generation
                    Complex RAG: Advanced with feedback loops and self-correction
                    """
                )

                # Streaming option
                st.subheader("Response Settings")
                streaming_enabled = st.toggle(
                    "Enable Streaming",
                    value=st.session_state.streaming_enabled,
                    help="Stream responses in real-time or wait for complete response"
                )
                st.session_state.streaming_enabled = streaming_enabled
                
                # LLM Configuration
                st.subheader("LLM Configuration")
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Higher values make output more random, lower values more deterministic"
                )
                
                # Retrieval Configuration
                st.subheader("Retrieval Configuration")
                k = st.slider(
                    "Number of Documents",
                    min_value=1,
                    max_value=10,
                    value=4,
                    help="Number of documents to retrieve"
                )
                
                # Additional parameters for complex agent
                agent_parameters = {}
                if agent_type == "Complex RAG":
                    st.subheader("Complex Agent Parameters")
                    max_retrievals = st.slider(
                        "Max Retrievals",
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="Maximum number of retrieval attempts"
                    )
                    max_generations = st.slider(
                        "Max Generations",
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="Maximum number of generation attempts"
                    )
                    recursion_limit = st.slider(
                            "Recursion Limit",
                            min_value=25,
                            max_value=100,
                            value=50,
                            help="Maximum number of state transitions in the agent"
                        )
                    agent_parameters.update({
                        "max_retrievals": max_retrievals,
                        "max_generations": max_generations,
                        "recursion_limit": recursion_limit
                    })
                
                # Update agent configuration
                st.session_state.agent_config = {
                    "llm": {
                        "name": "gpt-4o-mini",
                        "type": "openai",
                        "parameters": {
                            "temperature": temperature
                        }
                    },
                    "retriever": {
                        "collection_name": selected_collection,
                        "search_type": "similarity",
                        "k": k,
                        "search_parameters": {}
                    },
                    "agent_parameters": agent_parameters
                }
                
                return True
                
            except Exception as e:
                logger.error(f"Error rendering sidebar: {str(e)}")
                st.error(f"Error configuring agent: {str(e)}")
                return False

    def handle_streaming_response(self, response: AgentResponse) -> None:
        """Handle streaming response from agent"""
        try:
            message_placeholder = st.empty()
            full_response = ""
            retrieved_docs = []
            
            for chunk in response.iterate():
                if isinstance(chunk, dict):
                    if "error" in chunk:
                        st.error(f"Error in stream: {chunk['error']}")
                        break
                    elif "documents" in chunk:
                        retrieved_docs = chunk["documents"]
                        with st.expander("Retrieved Documents", expanded=False):
                            st.markdown(self._format_docs(retrieved_docs))
                    elif "generation" in chunk:
                        current_response = chunk["generation"]
                        full_response = current_response
                        message_placeholder.markdown(full_response)
                else:
                    logger.warning(f"Unexpected chunk format: {chunk}")
            
            if full_response:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })
            
        except Exception as e:
            logger.error(f"Error handling stream: {str(e)}", exc_info=True)
            st.error(f"Error processing response: {str(e)}")
    
    def handle_non_streaming_response(self, response: AgentResponse) -> None:
        """Handle non-streaming response from agent"""
        try:
            answer = response.get("answer")
            if answer:
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })
            else:
                st.error("No valid response received from agent")
                logger.error(f"Invalid response format: {response.data}")
        except Exception as e:
            logger.error(f"Error handling non-streaming response: {str(e)}", exc_info=True)
            st.error(f"Error processing response: {str(e)}")
    
    def handle_user_input(self):
        """Handle user input and agent interaction"""
        if prompt := st.chat_input("Your question"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            try:
                agent_type = "simple" if "Complex RAG" not in st.session_state.get("agent_config", {}).get("agent_parameters", {}) else "complex"
                streaming = st.session_state.streaming_enabled
                
                with st.chat_message("assistant"):
                    try:
                        response = self.agent_client.query_agent(
                            agent_type=agent_type,
                            question=prompt,
                            config=st.session_state.agent_config,
                            stream=streaming
                        )
                        
                        if streaming:
                            self.handle_streaming_response(response)
                        else:
                            with st.spinner("Generating response..."):
                                self.handle_non_streaming_response(response)
                                
                    except Exception as e:
                        logger.error(f"Error in agent interaction: {str(e)}", exc_info=True)
                        st.error(f"Error getting response from agent: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Error processing question: {str(e)}", exc_info=True)
                show_status_message(f"Error processing your question: {str(e)}", type="error")

    def render_chat_history(self):
        """Render chat message history"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def render(self):
        """Render the main chat interface"""
        st.title("Chat with RAG Agent 💬")
        
        # Configure agent first
        if not self.render_sidebar():
            return
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
            
        # Show chat interface
        self.render_chat_history()
        self.handle_user_input()

def main():
    st.set_page_config(
        page_title="Agent Chat",
        page_icon="💬",
        layout="wide"
    )
    
    chat_ui = ChatUI()
    chat_ui.render()

if __name__ == "__main__":
    main()
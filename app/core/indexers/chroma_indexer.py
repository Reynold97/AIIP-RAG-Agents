from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from chromadb import PersistentClient
from app.core.config.schemas import DatabaseConfig
from langchain_core.documents import Document
from app.core.config.schemas import DatabaseConfig, RetrieverConfig
from app.core.config.default_config import DEFAULT_DATABASE, DEFAULT_RETRIEVER
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging
import os

load_dotenv()
logger = logging.getLogger(__name__)

class ChromaDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDB, cls).__new__(cls)
            # Initialize with default configuration
            cls._instance._initialize_default()
        return cls._instance
    
    def _initialize_default(self):
        """Initialize with default settings"""
        self.embedding_function = OpenAIEmbeddings(model=DEFAULT_DATABASE.embedding.name)
        self.persist_directory = "./app/databases/chroma_db"
        self.client = None
        self.vectorstore = None
        
    def reconfigure(self, config: DatabaseConfig):
        """Reconfigure the database with new settings"""
        try:
            # Initialize embedding function based on config
            if config.embedding.type == "openai":
                self.embedding_function = OpenAIEmbeddings(
                    model=config.embedding.name,
                    **config.embedding.parameters
                )
            # Add other embedding types here as needed
            
            # Reset client and vectorstore
            self.client = None
            self.vectorstore = None
            
            # Connect with new configuration
            self._connect()
            logger.info("Database reconfigured successfully")
            
        except Exception as e:
            logger.error(f"Error reconfiguring database: {str(e)}")
            raise
        
    def _connect(self):
        """Create or connect to the ChromaDB client"""
        try:
            if not self.client:
                if not os.path.exists(self.persist_directory):
                    os.makedirs(self.persist_directory)
                self.client = PersistentClient(path=self.persist_directory)
        except Exception as e:
            logger.error(f"Error connecting to ChromaDB: {str(e)}")
            raise
    
    def initialize_db(self, collection_name="default_collection"):
        """Initialize or connect to a ChromaDB collection"""
        try:
            self._connect()
            
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory,
                client=self.client
            )
            return self.vectorstore
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
            
    def create_collection(self, collection_name: str):
        """Create a new collection"""
        try:
            self._connect()
            return self.initialize_db(collection_name)
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self._connect()
            if self.vectorstore and self.vectorstore._collection.name == collection_name:
                self.vectorstore = None
            self.client.delete_collection(collection_name)
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    def list_collections(self):
        """List all collections"""
        try:
            self._connect()
            return [col.name for col in self.client.list_collections()]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise

# Global instance initialized with default settings
chroma_db = ChromaDB()

class ChromaIndexer:
    def __init__(self, config: Optional[RetrieverConfig] = None):
        """Initialize ChromaIndexer with retriever configuration
        
        Args:
            config: RetrieverConfig for search operations. If None, uses default config.
        """
        self.config = config or DEFAULT_RETRIEVER
        self.vectorstore = chroma_db.initialize_db(self.config.collection_name)
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vectorstore"""
        self.vectorstore.add_documents(documents)
    
    def similarity_search(
        self, 
        query: str,
        config: Optional[RetrieverConfig] = None
    ):
        """Perform similarity search with optional retriever configuration
        
        Args:
            query: Search query string
            config: Optional RetrieverConfig to override default settings
        """
        try:
            search_config = config or self.config
            
            if search_config.search_type == "mmr":
                return self.vectorstore.max_marginal_relevance_search(
                    query,
                    k=search_config.k,
                    **search_config.search_parameters
                )
            else:  # default similarity search
                return self.vectorstore.similarity_search(
                    query,
                    k=search_config.k,
                    **search_config.search_parameters
                )
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise
    
    def update_document(self, document_id: str, document: Document):
        """Update a document in the vectorstore"""
        self.vectorstore.update_document(document_id, document)
    
    def delete_document(self, document_id: str):
        """Delete a document from the vectorstore"""
        self.vectorstore.delete([document_id])
    
    def as_retriever(self, config: Optional[RetrieverConfig] = None):
        """Get retriever with optional configuration
        
        Args:
            config: Optional RetrieverConfig to override default settings
        """
        try:
            search_config = config or self.config
            
            search_kwargs = {
                "k": search_config.k,
                **search_config.search_parameters
            }
            
            return self.vectorstore.as_retriever(
                search_type=search_config.search_type,
                search_kwargs=search_kwargs
            )
        except Exception as e:
            logger.error(f"Error creating retriever: {str(e)}")
            raise
    
    def count_documents(self):
        """Count documents in the collection"""
        return self.vectorstore._collection.count()
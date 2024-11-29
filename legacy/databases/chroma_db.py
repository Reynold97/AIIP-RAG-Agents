import os
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class ChromaDB:
    def __init__(self, persist_directory="./app/databases/chroma_db", embedding_function=OpenAIEmbeddings()):
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function
        self.client = None
        self.vectorstore = None
        
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
    
    def create_collection(self, collection_name):
        """Create a new collection"""
        try:
            self._connect()
            return self.initialize_db(collection_name)
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def delete_collection(self, collection_name):
        """Delete a collection"""
        try:
            self._connect()
            
            # Clear the vectorstore if it's the collection being deleted
            if self.vectorstore and self.vectorstore._collection.name == collection_name:
                self.vectorstore = None
            
            # Delete the collection
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

# Global instance
chroma_db = ChromaDB()
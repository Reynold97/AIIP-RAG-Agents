import os
import shutil
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class ChromaDB:
    def __init__(self, persist_directory="./app/databases/chroma_db", embedding_function=OpenAIEmbeddings()):
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function 
        self.client = PersistentClient(path=self.persist_directory)
        
    def initialize_db(self, collection_name="default_collection"):
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
        
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
            client=self.client
        )
        return self.vectorstore
    
    def load_db(self, collection_name="default_collection"):
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
            client=self.client
        )
    
    def delete_db(self):
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
    
    def create_collection(self, collection_name):
        return self.initialize_db(collection_name)
    
    def delete_collection(self, collection_name):
        self.client.delete_collection(collection_name)
    
    def list_collections(self):
        return [col.name for col in self.client.list_collections()]

chroma_db = ChromaDB()



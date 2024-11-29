from typing import List
from langchain_core.documents import Document
from app.databases.chroma_db import chroma_db

class ChromaIndexer:
    def __init__(self, collection_name="default_collection"):
        self.collection_name = collection_name
        self.vectorstore = chroma_db.initialize_db(collection_name)
    
    def add_documents(self, documents: List[Document]):
        self.vectorstore.add_documents(documents)
        #self.vectorstore.persist()
    
    def similarity_search(self, query: str, k: int = 4):
        return self.vectorstore.similarity_search(query, k=k)
    
    def update_document(self, document_id: str, document: Document):
        self.vectorstore.update_document(document_id, document)
        #self.vectorstore.persist()
    
    def delete_document(self, document_id: str):
        self.vectorstore.delete([document_id])
        #self.vectorstore.persist()
    
    def as_retriever(self, k: int = 4):
        """Return retriever initialized with specified number of documents to retrieve.
        
        Args:
            k (int): Number of documents to retrieve (default: 4)
        """
        search_kwargs = {"k": k}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    def get_collection(self):
        return chroma_db.load_db(self.collection_name)
    
    def count_documents(self):
        return self.vectorstore._collection.count()
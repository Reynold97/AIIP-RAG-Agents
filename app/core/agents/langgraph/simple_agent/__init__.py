from .agent import SimpleRAGAgent
from app.core.indexers.chroma_indexer import ChromaIndexer
from .chains import rag_chain

def create_chroma_simple_rag_agent(collection_name: str = "default_collection"):
    indexer = ChromaIndexer(collection_name)
    retriever = indexer.as_retriever()
    return SimpleRAGAgent(retriever, rag_chain)
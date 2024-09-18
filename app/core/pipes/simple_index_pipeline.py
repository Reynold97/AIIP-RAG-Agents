import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from app.core.chunkers.simple_chunker import SimpleChunker
from app.core.indexers.chroma_indexer import ChromaIndexer
from langchain_core.documents import Document

class SimpleIndexChromaPipeline:
    def __init__(self, collection_name: str, chunk_size: int = 10000, chunk_overlap: int = 200):
        self.collection_name = collection_name
        self.loader = PyPDFLoader
        self.chunker = SimpleChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.indexer = ChromaIndexer(collection_name=collection_name)

    def process_pdf(self, file_path: str) -> List[Document]:
        # Load PDF
        loader = self.loader(file_path)
        documents = loader.load()

        # Chunk documents
        chunked_documents = self.chunker.split_documents(documents)

        # Index documents
        self.indexer.add_documents(chunked_documents)

        return chunked_documents

    def process_multiple_pdfs(self, file_paths: List[str]) -> List[Document]:
        all_documents = []
        for file_path in file_paths:
            all_documents.extend(self.process_pdf(file_path))
        return all_documents

    def process_folder(self, folder_path: str) -> List[Document]:
        all_documents = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    all_documents.extend(self.process_pdf(file_path))
        return all_documents

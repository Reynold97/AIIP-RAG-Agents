import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from app.core.chunkers.simple_chunker import SimpleChunker
from app.core.indexers.chroma_indexer import ChromaIndexer
from app.core.config.schemas import RetrieverConfig
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class SimpleIndexChromaPipeline:
    def __init__(self, collection_name: str, chunk_size: int = 10000, chunk_overlap: int = 200):
        """Initialize the pipeline with collection name and chunking parameters.
        
        Args:
            collection_name: Name of the collection to store documents
            chunk_size: Size of document chunks (default: 10000)
            chunk_overlap: Overlap between chunks (default: 200)
        """
        try:
            # Create retriever config
            self.retriever_config = RetrieverConfig(collection_name=collection_name)
            
            self.collection_name = collection_name
            self.loader = PyPDFLoader
            self.chunker = SimpleChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            self.indexer = ChromaIndexer(self.retriever_config)
        except Exception as e:
            logger.error(f"Error initializing pipeline: {str(e)}")
            raise

    def process_pdf(self, file_path: str) -> List[Document]:
        """Process a single PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of processed Document objects
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
            Exception: For other processing errors
        """
        try:
            # Verify file exists and is PDF
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"File is not a PDF: {file_path}")
                
            logger.info(f"Processing PDF: {file_path}")
            
            # Load PDF
            loader = self.loader(file_path)
            documents = loader.load()
            
            if not documents:
                logger.warning(f"No content extracted from PDF: {file_path}")
                return []
            
            # Add file metadata to each document
            filename = os.path.basename(file_path)
            for doc in documents:
                doc.metadata.update({
                    "source_file": filename,
                    "file_path": file_path,
                    "page_number": doc.metadata.get("page", 1)
                })

            # Chunk documents
            chunked_documents = self.chunker.split_documents(documents)
            
            if not chunked_documents:
                logger.warning(f"No chunks created from PDF: {file_path}")
                return []
            
            # Ensure metadata is preserved in chunks
            for chunk in chunked_documents:
                if not chunk.metadata.get("source_file"):
                    chunk.metadata.update({
                        "source_file": filename,
                        "file_path": file_path,
                        "page_number": chunk.metadata.get("page", 1)
                    })

            # Index documents
            self.indexer.add_documents(chunked_documents)
            
            logger.info(f"Successfully processed PDF {filename} into {len(chunked_documents)} chunks")
            return chunked_documents

        except FileNotFoundError as e:
            logger.error(f"File not found error: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Invalid file error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise

    def process_multiple_pdfs(self, file_paths: List[str]) -> List[Document]:
        """Process multiple PDF files.
        
        Args:
            file_paths: List of paths to PDF files
            
        Returns:
            List of processed Document objects from all PDFs
            
        Raises:
            Exception: If any file processing fails
        """
        try:
            all_documents = []
            failed_files = []
            
            for file_path in file_paths:
                try:
                    processed_docs = self.process_pdf(file_path)
                    all_documents.extend(processed_docs)
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {str(e)}")
                    failed_files.append((file_path, str(e)))
            
            if failed_files:
                logger.warning(f"Failed to process {len(failed_files)} files")
                # Could raise an exception with failed files info if needed
                
            return all_documents
            
        except Exception as e:
            logger.error(f"Error in batch processing PDFs: {str(e)}")
            raise

    def process_folder(self, folder_path: str) -> List[Document]:
        """Process all PDF files in a folder.
        
        Args:
            folder_path: Path to folder containing PDF files
            
        Returns:
            List of processed Document objects from all PDFs
            
        Raises:
            NotADirectoryError: If folder_path is not a directory
            Exception: For other processing errors
        """
        try:
            if not os.path.isdir(folder_path):
                raise NotADirectoryError(f"Not a directory: {folder_path}")
                
            all_documents = []
            pdf_files = []
            
            # First collect all PDF files
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        pdf_files.append(file_path)
            
            if not pdf_files:
                logger.warning(f"No PDF files found in folder: {folder_path}")
                return []
                
            logger.info(f"Found {len(pdf_files)} PDF files in {folder_path}")
            
            # Process all collected PDFs
            return self.process_multiple_pdfs(pdf_files)
            
        except NotADirectoryError as e:
            logger.error(f"Directory error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {str(e)}")
            raise
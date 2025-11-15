import os
from typing import List, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFProcessor:
    """PDF processing service for loading and chunking documents."""

    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        self.upload_folder = settings.upload_folder

    def load_pdf(self, pdf_path: str, workspace_id: str) -> List[Document]:
        """
        Load and extract text from a single PDF.

        Args:
            pdf_path: Path to PDF file
            workspace_id: Workspace ID for metadata

        Returns:
            List of Document objects with text and metadata
        """
        try:
            logger.info(f"Loading PDF: {pdf_path}")

            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return []

            # Load PDF using PyPDFLoader
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()

            # Add workspace metadata
            file_name = os.path.basename(pdf_path)
            for page in pages:
                page.metadata.update({
                    "workspace_id": workspace_id,
                    "source": file_name,
                    "file_path": pdf_path,
                })

            logger.info(
                f"Successfully loaded {len(pages)} pages from {file_name}")
            return pages

        except Exception as e:
            logger.error(
                f"Error loading PDF {pdf_path}: {str(e)}", exc_info=True)
            return []

    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess extracted text.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())

        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        return text.strip()

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects
        """
        try:
            logger.info(f"Splitting {len(documents)} documents into chunks")

            # Clean text before splitting
            for doc in documents:
                doc.page_content = self.clean_text(doc.page_content)

            # Split documents
            chunks = self.text_splitter.split_documents(documents)

            logger.info(
                f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks

        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}", exc_info=True)
            return []

    def process_single_pdf(
        self,
        pdf_path: str,
        workspace_id: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> List[Document]:
        """
        Process a single PDF: load, clean, and chunk.

        Args:
            pdf_path: Path to PDF file
            workspace_id: Workspace ID
            progress_callback: Optional callback for progress updates

        Returns:
            List of processed Document chunks
        """
        start_time = time.time()

        try:
            # Update progress
            if progress_callback:
                progress_callback(pdf_path, 0.0)

            # Load PDF
            pages = self.load_pdf(pdf_path, workspace_id)
            if not pages:
                return []

            if progress_callback:
                progress_callback(pdf_path, 0.5)

            # Split into chunks
            chunks = self.split_documents(pages)

            if progress_callback:
                progress_callback(pdf_path, 1.0)

            elapsed_time = time.time() - start_time
            logger.info(
                f"Processed {os.path.basename(pdf_path)} in {elapsed_time:.2f}s: "
                f"{len(pages)} pages -> {len(chunks)} chunks"
            )

            return chunks

        except Exception as e:
            logger.error(
                f"Error processing PDF {pdf_path}: {str(e)}", exc_info=True)
            return []

    def process_pdfs(
        self,
        pdf_paths: List[str],
        workspace_id: str,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> List[Document]:
        """
        Process multiple PDFs in parallel.

        Args:
            pdf_paths: List of paths to PDF files
            workspace_id: Workspace ID
            max_workers: Maximum number of parallel workers
            progress_callback: Optional callback for progress updates

        Returns:
            Combined list of all Document chunks
        """
        logger.info(
            f"Processing {len(pdf_paths)} PDFs for workspace {workspace_id}")

        all_chunks = []

        # Process PDFs in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    self.process_single_pdf,
                    pdf_path,
                    workspace_id,
                    progress_callback
                )
                for pdf_path in pdf_paths
            ]

            for future in futures:
                chunks = future.result()
                all_chunks.extend(chunks)

        logger.info(
            f"Processed {len(pdf_paths)} PDFs: Total {len(all_chunks)} chunks")
        return all_chunks

    def get_pdf_paths(self, workspace_id: str, pdf_ids: List[str]) -> List[str]:
        """
        Get full paths to PDF files from IDs.

        Args:
            workspace_id: Workspace ID
            pdf_ids: List of PDF IDs

        Returns:
            List of full paths to PDF files
        """
        paths = []
        workspace_folder = Path(self.upload_folder) / workspace_id

        for pdf_id in pdf_ids:
            # Construct path: /uploads/{workspace_id}/{pdf_id}.pdf
            pdf_path = workspace_folder / f"{pdf_id}.pdf"
            if pdf_path.exists():
                paths.append(str(pdf_path))
            else:
                logger.warning(f"PDF not found: {pdf_path}")

        return paths

import os
import re
import hashlib
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import time

from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors"""
    pass


class PDFProcessor:
    """
    PDF processing service for loading and chunking documents.

    Features:
    - Parallel PDF processing
    - Text cleaning and normalization
    - Chunking with overlap
    - Document caching (1 hour TTL)
    - Progress callbacks
    - Comprehensive error handling
    - Support for multiple loaders (PyPDF, Unstructured)
    """

    def __init__(self, use_unstructured: bool = False, cache_ttl_minutes: int = 60):
        """
        Initialize PDF processor.

        Args:
            use_unstructured: Use UnstructuredPDFLoader instead of PyPDFLoader
            cache_ttl_minutes: Cache time-to-live in minutes
        """
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.use_unstructured = use_unstructured
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        self.upload_folder = settings.upload_folder

        # Cache for processed documents
        self._document_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"PDFProcessor initialized: chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}, "
            f"use_unstructured={use_unstructured}"
        )

    def load_pdf(self, pdf_path: str, workspace_id: str) -> List[Document]:
        """
        Load and extract text from a single PDF with comprehensive error handling.

        Args:
            pdf_path: Path to PDF file
            workspace_id: Workspace ID for metadata

        Returns:
            List of Document objects with text and metadata

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            PermissionError: If PDF file is not readable
        """
        try:
            logger.info(f"Loading PDF: {pdf_path}")

            # Validate file exists and is readable
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            if not os.access(pdf_path, os.R_OK):
                raise PermissionError(f"PDF file not readable: {pdf_path}")

            # Choose appropriate loader
            if self.use_unstructured:
                loader = UnstructuredPDFLoader(pdf_path)
                logger.debug(f"Using UnstructuredPDFLoader for {pdf_path}")
            else:
                loader = PyPDFLoader(pdf_path)
                logger.debug(f"Using PyPDFLoader for {pdf_path}")

            # Load PDF pages
            pages = loader.load()

            if not pages:
                logger.warning(f"No pages extracted from {pdf_path}")
                return []

            # Add enhanced metadata to each page
            file_name = os.path.basename(pdf_path)
            for i, page in enumerate(pages):
                page.metadata.update({
                    "workspace_id": workspace_id,
                    "source": file_name,
                    "file_path": pdf_path,
                    "page": i + 1,  # 1-indexed page numbers
                    "total_pages": len(pages),
                    "processed_at": datetime.utcnow().isoformat(),
                })

            logger.info(
                f"Successfully loaded {len(pages)} pages from {file_name}")
            return pages

        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"File access error for {pdf_path}: {str(e)}")
            raise

        except Exception as e:
            logger.error(
                f"Error loading PDF {pdf_path}: {str(e)}", exc_info=True)
            # Return empty list for partial results (graceful degradation)
            return []

    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess extracted text with advanced normalization.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""

        # Normalize line breaks (handle different OS formats)
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove multiple consecutive newlines (keep max 2 for paragraph separation)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove excessive whitespace while preserving single spaces
        text = re.sub(r'[ \t]+', ' ', text)

        # Handle special characters - remove non-printable characters
        text = ''.join(
            char for char in text if char.isprintable() or char in '\n\t')

        # Remove excessive spaces around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)

        # Fix common PDF extraction issues
        # Remove hyphenation at line breaks
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        # Normalize quotation marks
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks while preserving metadata.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects with enhanced metadata
        """
        try:
            logger.info(f"Splitting {len(documents)} documents into chunks")

            # Clean text before splitting
            cleaned_docs = []
            for doc in documents:
                cleaned_text = self.clean_text(doc.page_content)

                # Only include documents with meaningful content
                if cleaned_text and len(cleaned_text.strip()) > 50:
                    doc.page_content = cleaned_text
                    cleaned_docs.append(doc)
                else:
                    logger.debug(
                        f"Skipping page {doc.metadata.get('page')} from "
                        f"{doc.metadata.get('source')} - insufficient content"
                    )

            # Split documents into chunks
            chunks = self.text_splitter.split_documents(cleaned_docs)

            # Add chunk-specific metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_id": i,
                    "chunk_size": len(chunk.page_content),
                    "chunk_index": i,
                })

            logger.info(
                f"Created {len(chunks)} chunks from {len(cleaned_docs)} documents "
                f"(skipped {len(documents) - len(cleaned_docs)} pages)"
            )
            return chunks

        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}", exc_info=True)
            # Return original documents if splitting fails (fallback)
            return documents

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

    def load_and_process_pdfs(
        self,
        pdf_paths: List[str],
        workspace_id: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Document]:
        """
        Load and process multiple PDF files in parallel with caching.

        This is the main entry point for processing PDFs with comprehensive
        error handling and progress tracking.

        Args:
            pdf_paths: List of paths to PDF files
            workspace_id: Workspace identifier for metadata
            progress_callback: Optional callback function(current, total, filename)

        Returns:
            List of Document objects with chunks and metadata

        Raises:
            PDFProcessingError: If all PDFs fail to process
        """
        logger.info(
            f"Processing {len(pdf_paths)} PDFs for workspace {workspace_id}")

        all_documents = []
        processed_count = 0
        failed_pdfs = []

        # Process PDFs in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=settings.max_workers if hasattr(settings, 'max_workers') else 4) as executor:
            # Submit all tasks with caching
            future_to_pdf = {
                executor.submit(
                    self._process_single_pdf_with_cache,
                    pdf_path,
                    workspace_id
                ): pdf_path
                for pdf_path in pdf_paths
            }

            # Process completed tasks as they finish
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                processed_count += 1

                try:
                    documents = future.result()
                    if documents:
                        all_documents.extend(documents)
                        logger.info(
                            f"Successfully processed {pdf_path}: "
                            f"{len(documents)} chunks created"
                        )
                    else:
                        failed_pdfs.append(pdf_path)
                        logger.warning(f"No content extracted from {pdf_path}")

                except Exception as e:
                    failed_pdfs.append(pdf_path)
                    logger.error(
                        f"Failed to process {pdf_path}: {str(e)}",
                        exc_info=True
                    )

                # Call progress callback if provided
                if progress_callback:
                    filename = os.path.basename(pdf_path)
                    progress_callback(
                        processed_count, len(pdf_paths), filename)

        # Log summary
        success_count = len(pdf_paths) - len(failed_pdfs)
        logger.info(
            f"PDF processing complete: {success_count}/{len(pdf_paths)} succeeded, "
            f"{len(all_documents)} total chunks created"
        )

        if failed_pdfs:
            logger.warning(f"Failed PDFs: {', '.join(failed_pdfs)}")

        # Raise error if all PDFs failed
        if not all_documents and pdf_paths:
            raise PDFProcessingError(
                f"All {len(pdf_paths)} PDFs failed to process. "
                f"Check logs for details."
            )

        return all_documents

    def process_pdfs(
        self,
        pdf_paths: List[str],
        workspace_id: str,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> List[Document]:
        """
        Process multiple PDFs in parallel (legacy method for backward compatibility).

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
        failed_count = 0

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
                try:
                    chunks = future.result()
                    if chunks:
                        all_chunks.extend(chunks)
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"PDF processing failed: {str(e)}")

        logger.info(
            f"Processed {len(pdf_paths)} PDFs: "
            f"{len(all_chunks)} chunks, {failed_count} failures"
        )
        return all_chunks

    def _process_single_pdf_with_cache(
        self,
        pdf_path: str,
        workspace_id: str
    ) -> List[Document]:
        """
        Process a single PDF file with caching support.

        Args:
            pdf_path: Path to PDF file
            workspace_id: Workspace identifier

        Returns:
            List of Document chunks
        """
        # Check cache first
        cache_key = self._generate_cache_key(pdf_path, workspace_id)
        cached_result = self._get_from_cache(cache_key)

        if cached_result is not None:
            logger.debug(f"Cache hit for {pdf_path}")
            return cached_result

        try:
            # Load PDF
            documents = self.load_pdf(pdf_path, workspace_id)

            if not documents:
                logger.warning(f"No pages extracted from {pdf_path}")
                return []

            # Split into chunks
            chunks = self.split_documents(documents)

            # Cache the result
            self._add_to_cache(cache_key, chunks)

            return chunks

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            # Return empty list for partial results (graceful degradation)
            return []

    def _generate_cache_key(self, pdf_path: str, workspace_id: str) -> str:
        """
        Generate unique cache key for a PDF file.

        Args:
            pdf_path: Path to PDF file
            workspace_id: Workspace identifier

        Returns:
            Cache key string
        """
        try:
            # Include file modification time in cache key
            mtime = os.path.getmtime(pdf_path)
            key_string = f"{pdf_path}:{workspace_id}:{mtime}"
            return hashlib.md5(key_string.encode()).hexdigest()
        except Exception:
            # Fallback to simple key if mtime unavailable
            key_string = f"{pdf_path}:{workspace_id}"
            return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[List[Document]]:
        """
        Retrieve documents from cache if not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached documents or None
        """
        if cache_key in self._document_cache:
            cached_data = self._document_cache[cache_key]
            cached_time = cached_data["timestamp"]

            # Check if cache is still valid
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return cached_data["documents"]
            else:
                # Remove expired cache entry
                del self._document_cache[cache_key]

        return None

    def _add_to_cache(self, cache_key: str, documents: List[Document]) -> None:
        """
        Add documents to cache.

        Args:
            cache_key: Cache key
            documents: Documents to cache
        """
        self._document_cache[cache_key] = {
            "documents": documents,
            "timestamp": datetime.utcnow()
        }
        logger.debug(f"Added to cache: {cache_key} ({len(documents)} chunks)")

    def clear_cache(self) -> None:
        """Clear the document cache."""
        cache_size = len(self._document_cache)
        self._document_cache.clear()
        logger.info(f"Document cache cleared ({cache_size} entries removed)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_size": len(self._document_cache),
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60,
            "cached_keys": list(self._document_cache.keys())
        }

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


# Convenience function for backward compatibility
def load_and_process_pdfs(
    pdf_paths: List[str],
    workspace_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[Document]:
    """
    Convenience function to load and process PDFs.

    Args:
        pdf_paths: List of paths to PDF files
        workspace_id: Workspace identifier
        chunk_size: Maximum size of text chunks
        chunk_overlap: Number of overlapping tokens
        progress_callback: Optional callback for progress updates

    Returns:
        List of Document objects ready for embedding
    """
    processor = PDFProcessor()

    return processor.load_and_process_pdfs(
        pdf_paths=pdf_paths,
        workspace_id=workspace_id,
        progress_callback=progress_callback
    )

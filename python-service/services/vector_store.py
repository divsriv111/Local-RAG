import os
from typing import List, Optional
from pathlib import Path

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """Manager for vector database operations (ChromaDB)."""

    def __init__(self):
        self.db_type = settings.vector_db_type
        self.db_path = settings.vector_db_path
        self.embedding_model = self._initialize_embeddings()
        self.collections = {}  # Cache for collections

        # Ensure storage directory exists
        Path(self.db_path).mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized VectorStoreManager with {self.db_type} at {self.db_path}")

    def _initialize_embeddings(self):
        """
        Initialize embedding model based on configuration.

        Returns:
            Embedding model instance
        """
        try:
            if settings.use_local_embeddings or not settings.openai_api_key:
                logger.info("Using HuggingFace embeddings (local)")
                return HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-mpnet-base-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            else:
                logger.info("Using OpenAI embeddings")
                return OpenAIEmbeddings(
                    model=settings.embedding_model,
                    openai_api_key=settings.openai_api_key
                )
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            # Fall back to HuggingFace
            logger.info("Falling back to HuggingFace embeddings")
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )

    def _get_collection_name(self, workspace_id: str) -> str:
        """
        Get collection name for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Collection name
        """
        return f"workspace_{workspace_id}"

    def create_collection(self, workspace_id: str) -> Chroma:
        """
        Create or get collection for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Chroma collection instance
        """
        collection_name = self._get_collection_name(workspace_id)

        # Return cached collection if exists
        if collection_name in self.collections:
            logger.info(f"Using cached collection: {collection_name}")
            return self.collections[collection_name]

        try:
            # Create or load collection
            collection = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_model,
                persist_directory=self.db_path
            )

            # Cache collection
            self.collections[collection_name] = collection

            logger.info(f"Created/loaded collection: {collection_name}")
            return collection

        except Exception as e:
            logger.error(
                f"Error creating collection {collection_name}: {str(e)}")
            raise

    def add_documents(
        self,
        documents: List[Document],
        workspace_id: str,
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to vector store.

        Args:
            documents: List of Document objects
            workspace_id: Workspace ID
            batch_size: Number of documents to process at once

        Returns:
            True if successful, False otherwise
        """
        if not documents:
            logger.warning("No documents to add")
            return False

        try:
            collection = self.create_collection(workspace_id)

            logger.info(f"Adding {len(documents)} documents to collection")

            # Process in batches to avoid memory issues
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                collection.add_documents(batch)
                logger.info(
                    f"Added batch {i//batch_size + 1}: {len(batch)} documents")

            logger.info(
                f"Successfully added {len(documents)} documents to workspace {workspace_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}", exc_info=True)
            return False

    def similarity_search(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: Optional[List[str]] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Perform similarity search in vector store.

        Args:
            query: Search query
            workspace_id: Workspace ID
            pdf_ids: Optional list of PDF IDs to filter by
            k: Number of results to return

        Returns:
            List of relevant Document objects
        """
        try:
            collection = self.create_collection(workspace_id)

            # Build metadata filter for PDF IDs
            filter_dict = None
            if pdf_ids:
                # For ChromaDB, we need to check if source matches any PDF ID
                # This is a simplified approach - you may need to adjust based on your metadata structure
                logger.info(f"Filtering by PDF IDs: {pdf_ids}")

            # Perform similarity search
            if filter_dict:
                results = collection.similarity_search(
                    query=query,
                    k=k * 2,  # Get more results to filter
                    filter=filter_dict
                )
                # Manual filtering by PDF IDs
                results = [
                    doc for doc in results
                    if any(pdf_id in doc.metadata.get("source", "") for pdf_id in pdf_ids)
                ][:k]
            else:
                results = collection.similarity_search(query=query, k=k)

            logger.info(f"Found {len(results)} relevant documents for query")
            return results

        except Exception as e:
            logger.error(
                f"Error in similarity search: {str(e)}", exc_info=True)
            return []

    def similarity_search_with_score(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: Optional[List[str]] = None,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.

        Args:
            query: Search query
            workspace_id: Workspace ID
            pdf_ids: Optional list of PDF IDs to filter by
            k: Number of results to return

        Returns:
            List of tuples (Document, score)
        """
        try:
            collection = self.create_collection(workspace_id)

            # Perform similarity search with scores
            results = collection.similarity_search_with_score(query=query, k=k)

            # Filter by PDF IDs if specified
            if pdf_ids:
                results = [
                    (doc, score) for doc, score in results
                    if any(pdf_id in doc.metadata.get("source", "") for pdf_id in pdf_ids)
                ]

            logger.info(f"Found {len(results)} relevant documents with scores")
            return results

        except Exception as e:
            logger.error(
                f"Error in similarity search with score: {str(e)}", exc_info=True)
            return []

    def delete_collection(self, workspace_id: str) -> bool:
        """
        Delete collection for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if successful, False otherwise
        """
        try:
            collection_name = self._get_collection_name(workspace_id)

            # Remove from cache
            if collection_name in self.collections:
                del self.collections[collection_name]

            # Delete collection directory
            collection_path = Path(self.db_path) / collection_name
            if collection_path.exists():
                import shutil
                shutil.rmtree(collection_path)
                logger.info(f"Deleted collection: {collection_name}")

            return True

        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}", exc_info=True)
            return False

    def get_collection_size(self, workspace_id: str) -> int:
        """
        Get number of documents in collection.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of documents
        """
        try:
            collection = self.create_collection(workspace_id)
            count = collection._collection.count()
            return count
        except Exception as e:
            logger.error(f"Error getting collection size: {str(e)}")
            return 0

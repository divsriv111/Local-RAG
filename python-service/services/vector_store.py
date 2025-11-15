import os
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from functools import lru_cache

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

try:
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchAny
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """Manager for vector database operations (ChromaDB/Qdrant)."""

    def __init__(self, db_type: str = "chromadb"):
        """
        Initialize vector store manager.

        Args:
            db_type: Type of vector database ("chromadb" or "qdrant")
        """
        self.db_type = db_type.lower()
        self.db_path = settings.vector_db_path
        self.embedding_model = self._initialize_embeddings()
        self.collections = {}  # Cache for collections
        self.qdrant_client = None

        # Validate db_type
        if self.db_type == "qdrant" and not QDRANT_AVAILABLE:
            logger.warning("Qdrant not available, falling back to ChromaDB")
            self.db_type = "chromadb"

        # Ensure storage directory exists
        Path(self.db_path).mkdir(parents=True, exist_ok=True)

        # Initialize Qdrant client if needed
        if self.db_type == "qdrant":
            self._initialize_qdrant()

        logger.info(
            f"Initialized VectorStoreManager with {self.db_type} at {self.db_path}")

    def _initialize_qdrant(self):
        """Initialize Qdrant client for local storage."""
        try:
            if QDRANT_AVAILABLE:
                qdrant_path = Path(self.db_path.replace("chromadb", "qdrant"))
                qdrant_path.mkdir(parents=True, exist_ok=True)

                self.qdrant_client = QdrantClient(path=str(qdrant_path))
                logger.info(f"Initialized Qdrant client at {qdrant_path}")
            else:
                logger.error("Qdrant client not available")
        except Exception as e:
            logger.error(f"Error initializing Qdrant: {str(e)}")
            raise

    @lru_cache(maxsize=1)
    def _initialize_embeddings(self):
        """
        Initialize embedding model based on configuration.
        Uses caching to avoid re-initialization.

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

    def create_collection(self, workspace_id: str):
        """
        Create or get collection for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Vector store instance (Chroma or Qdrant)
        """
        collection_name = self._get_collection_name(workspace_id)

        # Return cached collection if exists
        if collection_name in self.collections:
            logger.info(f"Using cached collection: {collection_name}")
            return self.collections[collection_name]

        try:
            if self.db_type == "chromadb":
                collection = self._create_chroma_collection(collection_name)
            elif self.db_type == "qdrant":
                collection = self._create_qdrant_collection(collection_name)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            # Cache collection
            self.collections[collection_name] = collection

            logger.info(f"Created/loaded collection: {collection_name}")
            return collection

        except Exception as e:
            logger.error(
                f"Error creating collection {collection_name}: {str(e)}")
            raise

    def _create_chroma_collection(self, collection_name: str) -> Chroma:
        """
        Create ChromaDB collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Chroma instance
        """
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.db_path
        )

    def _create_qdrant_collection(self, collection_name: str):
        """
        Create Qdrant collection.

        Args:
            collection_name: Name of the collection

        Returns:
            QdrantVectorStore instance
        """
        if not QDRANT_AVAILABLE or not self.qdrant_client:
            raise RuntimeError("Qdrant is not available")

        # Get embedding dimension
        sample_embedding = self.embedding_model.embed_query("test")
        embedding_dim = len(sample_embedding)

        # Create collection if it doesn't exist
        collections = self.qdrant_client.get_collections().collections
        collection_names = [col.name for col in collections]

        if collection_name not in collection_names:
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {collection_name}")

        return QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=collection_name,
            embedding=self.embedding_model
        )

    def add_documents(
        self,
        documents: List[Document],
        workspace_id: str,
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to vector store with batch processing.

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

            # Enrich metadata for better filtering
            for doc in documents:
                if "workspace_id" not in doc.metadata:
                    doc.metadata["workspace_id"] = workspace_id
                # Ensure pdf_id is in metadata for filtering
                if "pdf_id" not in doc.metadata and "source" in doc.metadata:
                    # Extract PDF ID from source if available
                    doc.metadata["pdf_id"] = self._extract_pdf_id(
                        doc.metadata["source"])

            # Process in batches to avoid memory issues
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]

                if self.db_type == "chromadb":
                    collection.add_documents(batch)
                elif self.db_type == "qdrant":
                    # Qdrant batch processing
                    collection.add_documents(batch)

                logger.info(
                    f"Added batch {i//batch_size + 1}: {len(batch)} documents")

            logger.info(
                f"Successfully added {len(documents)} documents to workspace {workspace_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}", exc_info=True)
            return False

    async def add_documents_async(
        self,
        documents: List[Document],
        workspace_id: str,
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to vector store asynchronously.

        Args:
            documents: List of Document objects
            workspace_id: Workspace ID
            batch_size: Number of documents to process at once

        Returns:
            True if successful, False otherwise
        """
        # Run synchronous method in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.add_documents,
            documents,
            workspace_id,
            batch_size
        )

    def _extract_pdf_id(self, source: str) -> str:
        """
        Extract PDF ID from source path.

        Args:
            source: Source file path

        Returns:
            PDF ID or filename
        """
        # Extract filename without extension
        filename = Path(source).stem
        return filename

    def similarity_search(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: Optional[List[str]] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Perform similarity search in vector store with metadata filtering.

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

            if pdf_ids:
                logger.info(f"Filtering by PDF IDs: {pdf_ids}")

                if self.db_type == "chromadb":
                    results = self._chroma_search_with_filter(
                        collection, query, pdf_ids, k
                    )
                elif self.db_type == "qdrant":
                    results = self._qdrant_search_with_filter(
                        collection, query, pdf_ids, k
                    )
                else:
                    results = []
            else:
                results = collection.similarity_search(query=query, k=k)

            logger.info(f"Found {len(results)} relevant documents for query")
            return results

        except Exception as e:
            logger.error(
                f"Error in similarity search: {str(e)}", exc_info=True)
            return []

    def _chroma_search_with_filter(
        self,
        collection: Chroma,
        query: str,
        pdf_ids: List[str],
        k: int
    ) -> List[Document]:
        """
        Perform filtered search in ChromaDB.

        Args:
            collection: Chroma collection
            query: Search query
            pdf_ids: List of PDF IDs to filter by
            k: Number of results

        Returns:
            Filtered results
        """
        # ChromaDB filter - get more results and filter manually
        all_results = collection.similarity_search(query=query, k=k * 3)

        # Filter by PDF IDs
        filtered_results = [
            doc for doc in all_results
            if any(
                pdf_id in doc.metadata.get("source", "") or
                pdf_id == doc.metadata.get("pdf_id", "")
                for pdf_id in pdf_ids
            )
        ]

        return filtered_results[:k]

    def _qdrant_search_with_filter(
        self,
        collection,
        query: str,
        pdf_ids: List[str],
        k: int
    ) -> List[Document]:
        """
        Perform filtered search in Qdrant with payload filtering.

        Args:
            collection: Qdrant collection
            query: Search query
            pdf_ids: List of PDF IDs to filter by
            k: Number of results

        Returns:
            Filtered results
        """
        if not QDRANT_AVAILABLE:
            return []

        # Create Qdrant filter for PDF IDs
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="pdf_id",
                    match=MatchAny(any=pdf_ids)
                )
            ]
        )

        # Perform search with filter
        results = collection.similarity_search(
            query=query,
            k=k,
            filter=qdrant_filter
        )

        return results

    def similarity_search_with_score(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: Optional[List[str]] = None,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
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
            if pdf_ids:
                # Get more results for filtering
                results = collection.similarity_search_with_score(
                    query=query, k=k * 3)

                # Filter by PDF IDs
                filtered_results = [
                    (doc, score) for doc, score in results
                    if any(
                        pdf_id in doc.metadata.get("source", "") or
                        pdf_id == doc.metadata.get("pdf_id", "")
                        for pdf_id in pdf_ids
                    )
                ]
                results = filtered_results[:k]
            else:
                results = collection.similarity_search_with_score(
                    query=query, k=k)

            logger.info(f"Found {len(results)} relevant documents with scores")
            return results

        except Exception as e:
            logger.error(
                f"Error in similarity search with score: {str(e)}", exc_info=True)
            return []

    async def similarity_search_async(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: Optional[List[str]] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Perform similarity search asynchronously.

        Args:
            query: Search query
            workspace_id: Workspace ID
            pdf_ids: Optional list of PDF IDs to filter by
            k: Number of results to return

        Returns:
            List of relevant Document objects
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.similarity_search,
            query,
            workspace_id,
            pdf_ids,
            k
        )

    def hybrid_search(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: Optional[List[str]] = None,
        k: int = 5,
        sparse_weight: float = 0.3
    ) -> List[Document]:
        """
        Perform hybrid search (dense + sparse) for Qdrant.
        Falls back to regular similarity search for ChromaDB.

        Args:
            query: Search query
            workspace_id: Workspace ID
            pdf_ids: Optional list of PDF IDs to filter by
            k: Number of results to return
            sparse_weight: Weight for sparse search (0-1)

        Returns:
            List of relevant Document objects
        """
        if self.db_type == "qdrant" and QDRANT_AVAILABLE:
            try:
                # Qdrant supports hybrid search natively
                # This is a placeholder for hybrid search implementation
                logger.info("Performing hybrid search with Qdrant")
                # For now, fall back to similarity search
                # Full hybrid search would require additional configuration
                return self.similarity_search(query, workspace_id, pdf_ids, k)
            except Exception as e:
                logger.error(f"Error in hybrid search: {str(e)}")
                return []
        else:
            # ChromaDB doesn't support hybrid search, use regular similarity
            logger.info("Hybrid search not supported, using similarity search")
            return self.similarity_search(query, workspace_id, pdf_ids, k)

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

            if self.db_type == "chromadb":
                # Delete ChromaDB collection directory
                collection_path = Path(self.db_path) / collection_name
                if collection_path.exists():
                    import shutil
                    shutil.rmtree(collection_path)
                    logger.info(
                        f"Deleted ChromaDB collection: {collection_name}")

            elif self.db_type == "qdrant" and self.qdrant_client:
                # Delete Qdrant collection
                self.qdrant_client.delete_collection(collection_name)
                logger.info(f"Deleted Qdrant collection: {collection_name}")

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

            if self.db_type == "chromadb":
                count = collection._collection.count()
            elif self.db_type == "qdrant" and self.qdrant_client:
                collection_name = self._get_collection_name(workspace_id)
                collection_info = self.qdrant_client.get_collection(
                    collection_name)
                count = collection_info.points_count
            else:
                count = 0

            return count
        except Exception as e:
            logger.error(f"Error getting collection size: {str(e)}")
            return 0

    def get_collection_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics about a collection.

        Args:
            workspace_id: Workspace ID

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_name = self._get_collection_name(workspace_id)
            stats = {
                "collection_name": collection_name,
                "workspace_id": workspace_id,
                "db_type": self.db_type,
                "document_count": self.get_collection_size(workspace_id),
                "embedding_model": (
                    settings.embedding_model
                    if not settings.use_local_embeddings
                    else "sentence-transformers/all-mpnet-base-v2"
                )
            }

            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}

    def clear_cache(self):
        """Clear the collection cache."""
        self.collections.clear()
        logger.info("Cleared collection cache")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on vector store.

        Returns:
            Health check results
        """
        try:
            health = {
                "status": "healthy",
                "db_type": self.db_type,
                "db_path": self.db_path,
                "embedding_model": (
                    settings.embedding_model
                    if not settings.use_local_embeddings
                    else "sentence-transformers/all-mpnet-base-v2"
                ),
                "cached_collections": len(self.collections)
            }

            # Test embedding generation
            try:
                test_embedding = self.embedding_model.embed_query("test")
                health["embedding_dimension"] = len(test_embedding)
                health["embedding_test"] = "passed"
            except Exception as e:
                health["embedding_test"] = f"failed: {str(e)}"
                health["status"] = "unhealthy"

            # Test database connection
            if self.db_type == "qdrant" and self.qdrant_client:
                try:
                    collections = self.qdrant_client.get_collections()
                    health["qdrant_collections"] = len(collections.collections)
                except Exception as e:
                    health["qdrant_test"] = f"failed: {str(e)}"
                    health["status"] = "unhealthy"

            return health

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

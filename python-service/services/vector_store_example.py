"""
Example usage and testing for VectorStoreManager.

This module demonstrates how to use the VectorStoreManager class
for storing and retrieving document embeddings.
"""

import asyncio
from typing import List
from langchain.schema import Document

from vector_store import VectorStoreManager
from utils.logger import get_logger

logger = get_logger(__name__)


async def example_chromadb_usage():
    """Example using ChromaDB."""
    logger.info("=== ChromaDB Example ===")

    # Initialize with ChromaDB
    vector_store = VectorStoreManager(db_type="chromadb")

    # Create sample documents
    documents = [
        Document(
            page_content="Python is a high-level programming language.",
            metadata={
                "source": "python_guide.pdf",
                "page": 1,
                "pdf_id": "python_guide"
            }
        ),
        Document(
            page_content="FastAPI is a modern web framework for building APIs.",
            metadata={
                "source": "fastapi_docs.pdf",
                "page": 1,
                "pdf_id": "fastapi_docs"
            }
        ),
        Document(
            page_content="LangChain helps build applications with LLMs.",
            metadata={
                "source": "langchain_tutorial.pdf",
                "page": 1,
                "pdf_id": "langchain_tutorial"
            }
        ),
    ]

    # Test workspace ID
    workspace_id = "test-workspace-123"

    # Add documents
    success = await vector_store.add_documents_async(
        documents=documents,
        workspace_id=workspace_id
    )
    logger.info(f"Documents added: {success}")

    # Get collection stats
    stats = vector_store.get_collection_stats(workspace_id)
    logger.info(f"Collection stats: {stats}")

    # Perform similarity search
    query = "What is Python?"
    results = await vector_store.similarity_search_async(
        query=query,
        workspace_id=workspace_id,
        k=2
    )

    logger.info(f"Search results for '{query}':")
    for i, doc in enumerate(results, 1):
        logger.info(f"{i}. {doc.page_content[:100]}...")
        logger.info(f"   Metadata: {doc.metadata}")

    # Search with PDF filter
    results_filtered = await vector_store.similarity_search_async(
        query="web framework",
        workspace_id=workspace_id,
        pdf_ids=["fastapi_docs"],
        k=2
    )

    logger.info(f"Filtered search results:")
    for i, doc in enumerate(results_filtered, 1):
        logger.info(f"{i}. {doc.page_content[:100]}...")

    # Search with scores
    results_with_scores = vector_store.similarity_search_with_score(
        query="programming language",
        workspace_id=workspace_id,
        k=2
    )

    logger.info(f"Search results with scores:")
    for doc, score in results_with_scores:
        logger.info(f"Score: {score:.4f} - {doc.page_content[:100]}...")

    # Health check
    health = vector_store.health_check()
    logger.info(f"Health check: {health}")

    # Cleanup
    vector_store.delete_collection(workspace_id)
    logger.info("Collection deleted")


async def example_qdrant_usage():
    """Example using Qdrant."""
    logger.info("=== Qdrant Example ===")

    try:
        # Initialize with Qdrant
        vector_store = VectorStoreManager(db_type="qdrant")

        # Create sample documents
        documents = [
            Document(
                page_content="Machine learning is a subset of artificial intelligence.",
                metadata={
                    "source": "ml_basics.pdf",
                    "page": 1,
                    "pdf_id": "ml_basics"
                }
            ),
            Document(
                page_content="Neural networks are inspired by biological neurons.",
                metadata={
                    "source": "neural_networks.pdf",
                    "page": 1,
                    "pdf_id": "neural_networks"
                }
            ),
        ]

        workspace_id = "test-workspace-qdrant"

        # Add documents
        success = await vector_store.add_documents_async(
            documents=documents,
            workspace_id=workspace_id
        )
        logger.info(f"Documents added: {success}")

        # Perform similarity search
        results = await vector_store.similarity_search_async(
            query="What is machine learning?",
            workspace_id=workspace_id,
            k=2
        )

        logger.info(f"Search results:")
        for i, doc in enumerate(results, 1):
            logger.info(f"{i}. {doc.page_content}")

        # Hybrid search
        hybrid_results = vector_store.hybrid_search(
            query="neural networks",
            workspace_id=workspace_id,
            k=2
        )

        logger.info(f"Hybrid search results:")
        for i, doc in enumerate(hybrid_results, 1):
            logger.info(f"{i}. {doc.page_content}")

        # Cleanup
        vector_store.delete_collection(workspace_id)
        logger.info("Collection deleted")

    except Exception as e:
        logger.error(f"Qdrant example failed: {str(e)}")
        logger.info("Make sure Qdrant dependencies are installed")


async def example_batch_operations():
    """Example of batch operations and performance optimization."""
    logger.info("=== Batch Operations Example ===")

    vector_store = VectorStoreManager(db_type="chromadb")
    workspace_id = "test-batch-workspace"

    # Create many documents
    documents = []
    for i in range(100):
        doc = Document(
            page_content=f"This is document number {i} with some sample content.",
            metadata={
                "source": f"doc_{i % 10}.pdf",
                "page": i % 20,
                "pdf_id": f"doc_{i % 10}"
            }
        )
        documents.append(doc)

    logger.info(f"Adding {len(documents)} documents in batches...")

    # Add with custom batch size
    success = await vector_store.add_documents_async(
        documents=documents,
        workspace_id=workspace_id,
        batch_size=25
    )

    logger.info(f"Batch add completed: {success}")

    # Get stats
    stats = vector_store.get_collection_stats(workspace_id)
    logger.info(f"Collection stats: {stats}")

    # Test filtering by multiple PDFs
    search_results = await vector_store.similarity_search_async(
        query="sample content",
        workspace_id=workspace_id,
        pdf_ids=["doc_0", "doc_1", "doc_2"],
        k=5
    )

    logger.info(f"Found {len(search_results)} results filtered by PDFs")

    # Cleanup
    vector_store.delete_collection(workspace_id)
    vector_store.clear_cache()


async def example_error_handling():
    """Example of error handling."""
    logger.info("=== Error Handling Example ===")

    vector_store = VectorStoreManager(db_type="chromadb")

    # Try to search in non-existent workspace
    results = await vector_store.similarity_search_async(
        query="test",
        workspace_id="non-existent",
        k=5
    )
    logger.info(
        f"Search in non-existent workspace returned: {len(results)} results")

    # Try to add empty documents
    success = vector_store.add_documents(
        documents=[],
        workspace_id="test"
    )
    logger.info(f"Adding empty documents: {success}")

    # Test with invalid query
    try:
        results = await vector_store.similarity_search_async(
            query="",
            workspace_id="test",
            k=5
        )
        logger.info(f"Empty query returned: {len(results)} results")
    except Exception as e:
        logger.error(f"Empty query error: {str(e)}")


async def main():
    """Run all examples."""
    logger.info("Starting VectorStoreManager examples...")

    # Run examples
    await example_chromadb_usage()
    print("\n" + "="*50 + "\n")

    await example_qdrant_usage()
    print("\n" + "="*50 + "\n")

    await example_batch_operations()
    print("\n" + "="*50 + "\n")

    await example_error_handling()

    logger.info("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

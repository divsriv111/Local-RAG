"""
RAG Service Usage Examples

This file demonstrates how to use the RAG service with source citations.
"""

import time
from services.rag_service import RAGService


def example_basic_query():
    """Example 1: Basic query without chat history"""
    print("=" * 60)
    print("Example 1: Basic Query")
    print("=" * 60)

    rag = RAGService()

    result = rag.query(
        query="What are the key features of this product?",
        workspace_id="workspace-123",
        pdf_ids=["pdf-1", "pdf-2"],
        model_name="gpt-4o-mini",
        chat_history=None
    )

    print(f"\nAnswer:\n{result['answer']}\n")
    print(f"References: {result['references']}")
    print(f"Model: {result['model_used']}")
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
    print(f"Token Count: {result['token_count']}\n")


def example_streaming_query():
    """Example 2: Streaming query with real-time output"""
    print("=" * 60)
    print("Example 2: Streaming Query")
    print("=" * 60)

    rag = RAGService()

    print("\nStreaming response:\n")

    accumulated_answer = ""
    references = []

    for chunk in rag.query_stream(
        query="Explain the installation process",
        workspace_id="workspace-123",
        pdf_ids=["manual-pdf"],
        model_name="gpt-4-turbo",
        chat_history=[]
    ):
        if chunk["type"] == "source":
            print(f"[Source found: {chunk['pdf']}, Page {chunk['page']}]")

        elif chunk["type"] == "token":
            print(chunk["content"], end="", flush=True)
            accumulated_answer += chunk["content"]

        elif chunk["type"] == "done":
            references = chunk["references"]
            metadata = chunk["metadata"]
            print("\n")
            print(f"\nReferences: {references}")
            print(f"Processing Time: {metadata['processing_time_ms']:.2f}ms")

        elif chunk["type"] == "error":
            print(f"\nError: {chunk['message']}")
            break


def example_with_chat_history():
    """Example 3: Query with conversation context"""
    print("=" * 60)
    print("Example 3: Query with Chat History")
    print("=" * 60)

    rag = RAGService()

    # Simulated conversation history
    chat_history = [
        {
            "role": "user",
            "content": "What is machine learning?"
        },
        {
            "role": "assistant",
            "content": "Machine learning is a subset of AI that enables systems to learn from data. [Source: ml-guide.pdf, Page 3]"
        },
        {
            "role": "user",
            "content": "What are its applications?"
        },
        {
            "role": "assistant",
            "content": "Applications include image recognition, NLP, and predictive analytics. [Source: ml-guide.pdf, Page 15]"
        }
    ]

    # Follow-up question using context
    result = rag.query(
        query="Can you elaborate on the NLP applications?",
        workspace_id="workspace-456",
        pdf_ids=["ml-guide-pdf"],
        model_name="gpt-4-turbo",
        chat_history=chat_history
    )

    print(f"\nQuestion: Can you elaborate on the NLP applications?")
    print(f"\nAnswer:\n{result['answer']}\n")
    print(f"References: {result['references']}")


def example_generate_chat_title():
    """Example 4: Generate chat title from first query"""
    print("=" * 60)
    print("Example 4: Generate Chat Title")
    print("=" * 60)

    rag = RAGService()

    queries = [
        "How do I install Python on Windows?",
        "What are the benefits of using Docker containers?",
        "Explain quantum computing in simple terms"
    ]

    for query in queries:
        title = rag.generate_chat_name(query)
        print(f"\nQuery: {query}")
        print(f"Generated Title: {title}")


def example_error_handling():
    """Example 5: Error handling"""
    print("=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)

    rag = RAGService()

    try:
        result = rag.query(
            query="Test query",
            workspace_id="workspace-789",
            pdf_ids=["non-existent-pdf"],
            model_name="gpt-4o-mini",
            chat_history=None
        )

        # Check if no documents found
        if "don't have any relevant information" in result['answer']:
            print("\nNo relevant documents found for this query.")
            print(f"Response: {result['answer']}")
        else:
            print(f"\nAnswer: {result['answer']}")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")


def example_multiple_models():
    """Example 6: Comparing different models"""
    print("=" * 60)
    print("Example 6: Multiple Models Comparison")
    print("=" * 60)

    rag = RAGService()

    models = ["gpt-4o-mini", "gpt-4-turbo"]
    query = "What is the main topic of this document?"

    for model in models:
        try:
            print(f"\n--- Testing with {model} ---")

            result = rag.query(
                query=query,
                workspace_id="workspace-test",
                pdf_ids=["test-pdf"],
                model_name=model,
                chat_history=None
            )

            print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
            print(f"Token Count: {result['token_count']}")
            print(f"Answer Preview: {result['answer'][:100]}...")

        except Exception as e:
            print(f"Error with {model}: {str(e)}")


def example_streaming_with_progress():
    """Example 7: Streaming with progress tracking"""
    print("=" * 60)
    print("Example 7: Streaming with Progress Tracking")
    print("=" * 60)

    rag = RAGService()

    token_count = 0
    start_time = time.time()

    print("\nGenerating response...\n")

    for chunk in rag.query_stream(
        query="Describe the architecture",
        workspace_id="workspace-arch",
        pdf_ids=["architecture-pdf"],
        model_name="gpt-4o-mini",
        chat_history=[]
    ):
        if chunk["type"] == "token":
            print(chunk["content"], end="", flush=True)
            token_count += 1

        elif chunk["type"] == "done":
            elapsed = time.time() - start_time
            print("\n")
            print(f"\nGeneration completed:")
            print(f"  - Tokens: {token_count}")
            print(f"  - Time: {elapsed:.2f}s")
            print(f"  - Speed: {token_count / elapsed:.1f} tokens/sec")
            print(f"  - References: {len(chunk['references'])}")


def example_citation_formats():
    """Example 8: Various citation formats in responses"""
    print("=" * 60)
    print("Example 8: Citation Format Examples")
    print("=" * 60)

    # These are example responses that would be generated by the LLM
    example_responses = [
        "The answer is found in the manual [Source: user-manual.pdf, Page 5].",
        "According to the report (Source: annual-report.pdf, Page 12), revenue increased.",
        "Key findings [guide.pdf, Page 8] indicate positive trends.",
        "The specification [spec.pdf, p. 23] defines the requirements."
    ]

    rag = RAGService()

    # Mock retrieved documents for testing
    from langchain.schema import Document
    mock_docs = [
        (Document(page_content="test", metadata={
         "source": "test.pdf", "page": 1}), 0.9)
    ]

    print("\nTesting citation extraction patterns:\n")

    for response in example_responses:
        references = rag._extract_citations(response, mock_docs)
        print(f"Response: {response}")
        print(f"Extracted: {references}\n")


# Import time for example 7


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RAG SERVICE USAGE EXAMPLES")
    print("=" * 60 + "\n")

    # Run examples
    # Note: These examples require actual vector store data and API keys
    # Uncomment the examples you want to run

    # example_basic_query()
    # example_streaming_query()
    # example_with_chat_history()
    # example_generate_chat_title()
    # example_error_handling()
    # example_multiple_models()
    # example_streaming_with_progress()
    example_citation_formats()  # This one works without external dependencies

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")

"""
Test script for streaming LLM endpoint.

This script demonstrates how to consume the streaming API endpoint
and handle Server-Sent Events (SSE) properly.
"""

import json
import requests
import sseclient  # pip install sseclient-py
from typing import Dict, Any


def test_streaming_query():
    """Test the streaming LLM query endpoint."""

    # API endpoint
    url = "http://localhost:8000/api/llm/query"

    # Request payload
    payload = {
        "query": "What are the main findings in the research paper?",
        "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
        "pdf_ids": ["pdf-001", "pdf-002"],
        "chat_history_id": "chat-001",
        "model_name": "gpt-4o-mini",
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"}
        ]
    }

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }

    print("🚀 Starting streaming request...\n")

    try:
        # Make POST request with streaming enabled
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=300  # 5 minutes timeout
        )

        # Check response status
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return

        print(f"✅ Connected! Status: {response.status_code}")
        print(
            f"📊 Correlation ID: {response.headers.get('X-Correlation-ID', 'N/A')}\n")

        # Parse SSE stream
        client = sseclient.SSEClient(response)

        accumulated_answer = ""
        sources = []

        for event in client.events():
            if event.data:
                try:
                    chunk = json.loads(event.data)
                    chunk_type = chunk.get("type")

                    if chunk_type == "token":
                        # Print token as it arrives
                        token = chunk.get("content", "")
                        print(token, end="", flush=True)
                        accumulated_answer += token

                    elif chunk_type == "source":
                        # Collect source references
                        pdf = chunk.get("pdf", "unknown")
                        page = chunk.get("page", 0)
                        score = chunk.get("relevance_score", 0.0)
                        sources.append({
                            "pdf": pdf,
                            "page": page,
                            "score": score
                        })
                        print(
                            f"\n\n📄 Source: {pdf}, Page: {page} (Score: {score:.2f})")

                    elif chunk_type == "done":
                        # Final chunk with complete answer and metadata
                        print("\n\n✅ Stream completed!")

                        answer = chunk.get("answer", accumulated_answer)
                        references = chunk.get("references", [])
                        metadata = chunk.get("metadata", {})

                        print("\n" + "="*60)
                        print("📝 FINAL ANSWER:")
                        print("="*60)
                        print(answer)

                        if references:
                            print("\n" + "="*60)
                            print("📚 REFERENCES:")
                            print("="*60)
                            for ref in references:
                                pdf = ref.get("pdf", "unknown")
                                page = ref.get("page", 0)
                                score = ref.get("relevance_score", "N/A")
                                print(
                                    f"  • {pdf}, Page {page} (Score: {score})")

                        if metadata:
                            print("\n" + "="*60)
                            print("ℹ️  METADATA:")
                            print("="*60)
                            for key, value in metadata.items():
                                print(f"  • {key}: {value}")

                        break

                    elif chunk_type == "error":
                        # Error occurred during streaming
                        error_msg = chunk.get("message", "Unknown error")
                        print(f"\n\n❌ Error: {error_msg}")
                        break

                    else:
                        print(f"\n⚠️  Unknown chunk type: {chunk_type}")

                except json.JSONDecodeError as e:
                    print(f"\n⚠️  Failed to parse chunk: {e}")
                    print(f"Raw data: {event.data}")

        print("\n\n✨ Done!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def test_streaming_simple():
    """Simple test without SSE client library."""

    url = "http://localhost:8000/api/llm/query"

    payload = {
        "query": "Summarize the key points.",
        "workspace_id": "test-workspace",
        "pdf_ids": ["pdf-001"],
        "chat_history_id": "test-chat",
        "model_name": "gpt-4o-mini",
        "chat_history": []
    }

    print("🚀 Testing simple streaming...\n")

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=300
        )

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return

        print("✅ Connected!\n")

        # Read line by line
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')

                # SSE format: "data: {json}"
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix

                    try:
                        chunk = json.loads(data_str)
                        chunk_type = chunk.get("type")

                        if chunk_type == "token":
                            print(chunk.get("content", ""), end="", flush=True)
                        elif chunk_type == "source":
                            print(
                                f"\n[Source: {chunk.get('pdf')}, Page {chunk.get('page')}]")
                        elif chunk_type == "done":
                            print("\n\n✅ Done!")
                            break
                        elif chunk_type == "error":
                            print(f"\n❌ Error: {chunk.get('message')}")
                            break

                    except json.JSONDecodeError:
                        pass

        print("\n✨ Streaming completed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 STREAMING LLM ENDPOINT TEST")
    print("=" * 60)
    print()

    # Choose test method
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        test_streaming_simple()
    else:
        print("ℹ️  Using SSE client library (recommended)")
        print("   For simple test, run: python test_streaming.py simple\n")
        test_streaming_query()

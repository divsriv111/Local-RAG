import re
import time
from typing import List, Dict, Generator, Optional

from langchain.schema import Document

from services.llm_service import LLMManager
from services.vector_store import VectorStoreManager
from models.response_models import SourceReference
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """RAG service for retrieval-augmented generation with citations."""

    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.llm_manager = LLMManager()
        self.retrieval_top_k = settings.retrieval_top_k

    def query(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: List[str],
        model_name: str,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Process RAG query and generate response.

        Args:
            query: User query
            workspace_id: Workspace ID
            pdf_ids: List of PDF IDs to search
            model_name: LLM model to use
            chat_history: Previous conversation messages

        Returns:
            Dictionary with answer, references, and metadata
        """
        start_time = time.time()

        try:
            logger.info(f"Processing RAG query for workspace {workspace_id}")

            # Step 1: Retrieve relevant documents
            logger.info("Retrieving relevant documents...")
            retrieved_docs = self.vector_store.similarity_search_with_score(
                query=query,
                workspace_id=workspace_id,
                pdf_ids=pdf_ids,
                k=self.retrieval_top_k
            )

            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I don't have any relevant information to answer this question.",
                    "references": [],
                    "model_used": model_name,
                    "processing_time_ms": (time.time() - start_time) * 1000
                }

            # Step 2: Format context and chat history
            context = self._format_context(retrieved_docs)
            formatted_history = self._format_chat_history(chat_history)

            # Step 3: Generate response
            logger.info(f"Generating response with {model_name}...")
            response_text = self.llm_manager.generate_response(
                query=query,
                context=context,
                model_name=model_name,
                chat_history=chat_history
            )

            # Step 4: Extract citations from response
            references = self._extract_citations(response_text, retrieved_docs)

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"RAG query completed in {processing_time:.2f}ms")

            return {
                "answer": response_text,
                "references": references,
                "model_used": model_name,
                "processing_time_ms": processing_time,
                "token_count": len(response_text.split())  # Rough estimate
            }

        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
            raise

    def query_stream(
        self,
        query: str,
        workspace_id: str,
        pdf_ids: List[str],
        model_name: str,
        chat_history: Optional[List[Dict]] = None
    ) -> Generator[Dict, None, None]:
        """
        Process RAG query with streaming response.

        Args:
            query: User query
            workspace_id: Workspace ID
            pdf_ids: List of PDF IDs to search
            model_name: LLM model to use
            chat_history: Previous conversation messages

        Yields:
            Dictionaries with streaming chunks
        """
        start_time = time.time()

        try:
            logger.info(
                f"Processing streaming RAG query for workspace {workspace_id}")

            # Step 1: Retrieve relevant documents
            logger.info("Retrieving relevant documents...")
            retrieved_docs = self.vector_store.similarity_search_with_score(
                query=query,
                workspace_id=workspace_id,
                pdf_ids=pdf_ids,
                k=self.retrieval_top_k
            )

            if not retrieved_docs:
                logger.warning("No relevant documents found")
                yield {
                    "type": "done",
                    "answer": "I don't have any relevant information to answer this question.",
                    "references": [],
                    "metadata": {"model_used": model_name}
                }
                return

            # Step 2: Send source references first
            for doc, score in retrieved_docs[:3]:  # Send top 3 sources
                source = doc.metadata.get("source", "unknown")
                page = doc.metadata.get("page", 0)
                yield {
                    "type": "source",
                    "pdf": source,
                    "page": page,
                    "relevance_score": float(score)
                }

            # Step 3: Format context and chat history
            context = self._format_context(retrieved_docs)
            formatted_history = self._format_chat_history(chat_history)

            # Step 4: Stream response
            logger.info(f"Streaming response with {model_name}...")
            accumulated_response = ""

            for token in self.llm_manager.generate_response_stream(
                query=query,
                context=context,
                model_name=model_name,
                chat_history=chat_history
            ):
                accumulated_response += token
                yield {
                    "type": "token",
                    "content": token
                }

            # Step 5: Extract citations and send final chunk
            references = self._extract_citations(
                accumulated_response, retrieved_docs)

            processing_time = (time.time() - start_time) * 1000

            yield {
                "type": "done",
                "answer": accumulated_response,
                "references": references,
                "metadata": {
                    "model_used": model_name,
                    "processing_time_ms": processing_time,
                    "token_count": len(accumulated_response.split())
                }
            }

            logger.info(
                f"Streaming RAG query completed in {processing_time:.2f}ms")

        except Exception as e:
            logger.error(
                f"Error in streaming RAG query: {str(e)}", exc_info=True)
            yield {
                "type": "error",
                "message": str(e)
            }

    def _format_context(self, retrieved_docs: List[tuple]) -> str:
        """
        Format retrieved documents into context string with source information.

        Args:
            retrieved_docs: List of (Document, score) tuples

        Returns:
            Formatted context string with source citations
        """
        context_parts = []

        for i, (doc, score) in enumerate(retrieved_docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", 0)
            content = doc.page_content

            # Format with clear source attribution for citation
            context_parts.append(
                f"[Document {i} - Source: {source}, Page {page}]\n{content}\n"
            )

        return "\n\n".join(context_parts)

    def _format_chat_history(self, chat_history: Optional[List[Dict]]) -> str:
        """
        Format chat history for inclusion in prompt.
        Includes last 5 messages from conversation.

        Args:
            chat_history: List of message dictionaries with 'role' and 'content'

        Returns:
            Formatted chat history string
        """
        if not chat_history:
            return "No previous conversation."

        # Take last 5 messages
        recent_history = chat_history[-5:]
        history_lines = []

        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                history_lines.append(f"User: {content}")
            elif role == "assistant":
                history_lines.append(f"Assistant: {content}")

        return "\n".join(history_lines) if history_lines else "No previous conversation."

    def _extract_citations(
        self,
        response_text: str,
        retrieved_docs: List[tuple]
    ) -> List[Dict]:
        """
        Extract source citations from response text using multiple patterns.

        Supported patterns:
        - [Source: filename.pdf, Page X]
        - [Source: filename.pdf, Page: X]
        - (Source: filename.pdf, Page X)

        Args:
            response_text: Generated response text
            retrieved_docs: Retrieved documents with scores

        Returns:
            List of source reference dictionaries with 'pdf' and 'page' keys
        """
        references = []
        seen_sources = set()

        # Multiple citation patterns to support various formats
        citation_patterns = [
            # [Source: file.pdf, Page X] or Page: X
            r'\[Source:\s*([^,]+),\s*Page\s*:?\s*(\d+)\]',
            # (Source: file.pdf, Page X)
            r'\(Source:\s*([^,]+),\s*Page\s*:?\s*(\d+)\)',
            # [file.pdf, Page X]
            r'\[([^\]]+\.pdf),\s*(?:p|P)age\s*:?\s*(\d+)\]',
            # [file.pdf, p. X] or [file.pdf, p X]
            r'\[([^\]]+\.pdf),\s*(?:p|P)\.?\s*(\d+)\]',
        ]

        # Try all patterns
        for pattern in citation_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)

            for pdf, page in matches:
                pdf = pdf.strip()
                # Handle .pdf extension if missing
                if not pdf.lower().endswith('.pdf'):
                    pdf = pdf + '.pdf'

                try:
                    page = int(page)
                except ValueError:
                    continue

                source_key = f"{pdf}_{page}"

                if source_key not in seen_sources:
                    references.append({
                        "pdf": pdf,
                        "page": page
                    })
                    seen_sources.add(source_key)

        # If no citations found in text, add sources from retrieved docs
        # This ensures we always have references even if LLM didn't cite properly
        if not references:
            logger.info(
                "No citations found in response, using retrieved documents")
            for doc, score in retrieved_docs[:3]:  # Top 3 most relevant
                source = doc.metadata.get("source", "unknown")
                page = doc.metadata.get("page", 0)

                # Extract filename from path if needed
                if '/' in source or '\\' in source:
                    source = source.split('/')[-1].split('\\')[-1]

                source_key = f"{source}_{page}"

                if source_key not in seen_sources:
                    references.append({
                        "pdf": source,
                        "page": page,
                        "relevance_score": float(score)
                    })
                    seen_sources.add(source_key)

        logger.info(f"Extracted {len(references)} citation references")
        return references

    def generate_chat_name(self, first_query: str) -> str:
        """
        Generate a chat name from the first query.

        Args:
            first_query: First user query

        Returns:
            Generated chat name
        """
        try:
            # Use LLM to generate a concise title
            prompt = f"""Generate a short, concise title (3-5 words) for a conversation that starts with this question:

"{first_query}"

Return ONLY the title, nothing else."""

            response = self.llm_manager.generate_response(
                query=prompt,
                context="",
                model_name=settings.default_llm_model,
                chat_history=None
            )

            # Clean up response
            title = response.strip().strip('"').strip("'")

            # Fallback to truncated query if title is too long
            if len(title) > 50:
                title = first_query[:47] + "..."

            return title

        except Exception as e:
            logger.error(f"Error generating chat name: {str(e)}")
            # Fallback to truncated query
            return first_query[:47] + "..." if len(first_query) > 50 else first_query

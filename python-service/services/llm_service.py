from typing import Generator, Optional, Dict, Any
import time

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.schema.language_model import BaseChatModel

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    """Manager for LLM operations supporting multiple models."""

    def __init__(self):
        self.default_model = settings.default_llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.max_tokens
        self.openai_api_key = settings.openai_api_key
        self.local_llm_base_url = settings.local_llm_base_url
        self.ollama_base_url = settings.ollama_base_url

        # Cache for LLM instances
        self._llm_cache: Dict[str, BaseChatModel] = {}

    def get_llm(self, model_name: str) -> BaseChatModel:
        """
        Get LLM instance based on model name.

        Supports:
        - GPT models: "gpt-4-turbo", "gpt-4.1-mini" (gpt-4o-mini)
        - Local models via Ollama: "local-llama-3", "local-mistral"
        - Local models via LMStudio: Uses OpenAI-compatible API with fallback to Ollama

        Args:
            model_name: Name of the model to use

        Returns:
            BaseChatModel instance ready for RAG chain

        Raises:
            ValueError: If model is not supported or unavailable
        """
        # Check cache first
        cache_key = f"{model_name}"
        if cache_key in self._llm_cache:
            logger.debug(f"Returning cached LLM for model: {model_name}")
            return self._llm_cache[cache_key]

        model = model_name or self.default_model
        logger.info(f"Initializing LLM: {model}")

        try:
            llm = None

            # OpenAI models (GPT-4, GPT-4o-mini, etc.)
            if model.startswith("gpt-") or model.startswith("o1-"):
                llm = self._get_openai_llm(model)

            # Local models (try LMStudio first, fallback to Ollama)
            elif model.startswith("local-"):
                llm = self._get_local_llm(model)

            # Default to gpt-4o-mini
            else:
                logger.warning(
                    f"Unknown model {model}, defaulting to gpt-4o-mini")
                llm = self._get_openai_llm("gpt-4o-mini")

            # Cache the LLM instance
            self._llm_cache[cache_key] = llm
            logger.info(
                f"LLM instance created and cached for model: {model_name}")

            return llm

        except Exception as e:
            logger.error(
                f"Error initializing LLM {model}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to initialize model '{model}': {str(e)}")

    def _get_openai_llm(self, model_name: str) -> ChatOpenAI:
        """
        Get OpenAI ChatGPT model instance with streaming support.

        Args:
            model_name: OpenAI model name

        Returns:
            ChatOpenAI instance with streaming enabled
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        # Map model names to OpenAI model IDs
        model_map = {
            'gpt-4-turbo': 'gpt-4-turbo-preview',
            'gpt-4.1-mini': 'gpt-4o-mini',
            'gpt-4o-mini': 'gpt-4o-mini',
            'gpt-4': 'gpt-4',
            'gpt-3.5-turbo': 'gpt-3.5-turbo'
        }

        openai_model_id = model_map.get(model_name, model_name)

        logger.info(f"Initializing OpenAI model: {openai_model_id}")

        return ChatOpenAI(
            model=openai_model_id,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=self.openai_api_key,
            streaming=True,
            request_timeout=120,
            max_retries=3
        )

    def _get_local_llm(self, model_name: str) -> BaseChatModel:
        """
        Get local model instance with LMStudio fallback to Ollama.

        Args:
            model_name: Local model name (e.g., 'local-llama-3', 'local-mistral')

        Returns:
            Local LLM instance
        """
        # Extract actual model name
        actual_model = model_name.replace('local-', '')

        # Try LMStudio first (OpenAI-compatible API)
        try:
            logger.info(
                f"Attempting to connect to LMStudio for model: {actual_model}")

            llm = ChatOpenAI(
                model=actual_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                base_url=self.local_llm_base_url,
                api_key='lm-studio',  # LMStudio doesn't require real API key
                streaming=True,
                request_timeout=120
            )

            # Test connection with a simple query
            llm.invoke([HumanMessage(content="test")])
            logger.info(
                f"Successfully connected to LMStudio for model: {actual_model}")
            return llm

        except Exception as e:
            logger.warning(
                f"LMStudio unavailable: {str(e)}, falling back to Ollama")

            # Fall back to Ollama
            return self._get_ollama_llm(actual_model)

    def _get_ollama_llm(self, model_name: str) -> ChatOllama:
        """
        Get Ollama model instance.

        Args:
            model_name: Ollama model name (e.g., 'llama-3', 'mistral')

        Returns:
            ChatOllama instance
        """
        # Map common names to Ollama model names
        model_map = {
            'llama-3': 'llama3',
            'llama3': 'llama3',
            'mistral': 'mistral',
            'codellama': 'codellama',
            'phi': 'phi'
        }

        ollama_model = model_map.get(model_name, model_name)

        logger.info(f"Initializing Ollama model: {ollama_model}")

        try:
            return ChatOllama(
                model=ollama_model,
                temperature=self.temperature,
                base_url=self.ollama_base_url
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Ollama model '{ollama_model}': {str(e)}")
            raise ValueError(f"Ollama model '{ollama_model}' is not available. "
                             f"Please ensure Ollama is running and the model is pulled.")

    def generate_response(
        self,
        query: str,
        context: str,
        model_name: str,
        chat_history: Optional[list] = None
    ) -> str:
        """
        Generate non-streaming response from LLM.

        Args:
            query: User query
            context: Context from retrieved documents
            model_name: Model to use (required)
            chat_history: Previous conversation messages

        Returns:
            Generated response text
        """
        start_time = time.time()
        token_count = 0

        try:
            llm = self.get_llm(model_name)

            # Build messages
            messages = self._build_messages(query, context, chat_history)

            # Generate response
            logger.info(f"Generating response with {model_name}")
            response = llm.invoke(messages)

            # Extract text from response
            if hasattr(response, "content"):
                response_text = response.content
                token_count = len(response_text.split())
            else:
                response_text = str(response)
                token_count = len(response_text.split())

            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"Generated response - Model: {model_name}, "
                f"Latency: {elapsed_time:.2f}ms, Tokens: {token_count}"
            )

            return response_text

        except Exception as e:
            logger.error(
                f"Error generating response with {model_name}: {str(e)}", exc_info=True)
            return f"Error: Unable to generate response. {str(e)}"

    def generate_response_stream(
        self,
        query: str,
        context: str,
        model_name: str,
        chat_history: Optional[list] = None
    ) -> Generator[str, None, None]:
        """
        Generate streaming response from LLM with real-time token generation.

        Args:
            query: User query
            context: Context from retrieved documents
            model_name: Model to use (required)
            chat_history: Previous conversation messages

        Yields:
            Response tokens as they are generated
        """
        start_time = time.time()
        token_count = 0

        try:
            llm = self.get_llm(model_name)

            # Build messages
            messages = self._build_messages(query, context, chat_history)

            logger.info(f"Starting streaming response with {model_name}")

            # Stream response
            for chunk in llm.stream(messages):
                if hasattr(chunk, "content"):
                    token = chunk.content
                    token_count += 1
                    yield token
                else:
                    token = str(chunk)
                    token_count += 1
                    yield token

            # Log metrics after completion
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"Streaming response completed - Model: {model_name}, "
                f"Latency: {elapsed_time:.2f}ms, Tokens: {token_count}"
            )

        except Exception as e:
            logger.error(
                f"Error streaming response with {model_name}: {str(e)}", exc_info=True)
            yield f"\n\nError: Unable to generate response. {str(e)}"

    def _build_messages(
        self,
        query: str,
        context: str,
        chat_history: Optional[list] = None
    ) -> list:
        """
        Build message list for LLM using LangChain message types.

        Args:
            query: User query
            context: Context from documents
            chat_history: Previous messages

        Returns:
            List of LangChain message objects
        """
        # System prompt
        system_prompt = """You are a helpful AI assistant. Answer the user's question based ONLY on the provided context from PDF documents.

Instructions:
- Provide accurate and detailed answers based on the context
- If the answer is not in the context, say "I don't have enough information to answer this question."
- Cite sources using [Source: filename.pdf, Page X] format
- Use markdown formatting for better readability (bold, italic, lists, code blocks)
- Be concise but thorough
- Include clickable references at the end

Always ground your answers in the provided context."""

        # Format chat history
        history_text = ""
        if chat_history:
            history_lines = []
            for msg in chat_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    history_lines.append(f"User: {content}")
                else:
                    history_lines.append(f"Assistant: {content}")
            history_text = "\n".join(history_lines)

        # Build user message with context and query
        user_message = f"""Context from PDF documents:
{context}

Previous conversation:
{history_text}

Question: {query}"""

        # Return messages as LangChain message objects
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

    def test_model_availability(self, model_name: str) -> Dict[str, Any]:
        """
        Test if a model is available and working.

        Args:
            model_name: Model to test

        Returns:
            Dictionary with test results including availability, latency, and response
        """
        try:
            start_time = time.time()
            llm = self.get_llm(model_name)

            # Send simple test query
            response = llm.invoke([HumanMessage(content="Say 'Hello'")])

            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            latency = (time.time() - start_time) * 1000

            return {
                'model': model_name,
                'available': True,
                'latency_ms': round(latency, 2),
                'response': response_text[:50] if response_text else ""
            }

        except Exception as e:
            logger.error(f"Model {model_name} test failed: {str(e)}")
            return {
                'model': model_name,
                'available': False,
                'error': str(e)
            }

    def clear_cache(self):
        """Clear LLM instance cache"""
        self._llm_cache.clear()
        logger.info("LLM cache cleared")

    def get_available_models(self) -> list[dict]:
        """
        Get list of available models with their status.

        Returns:
            List of model info dictionaries with name, status, and provider
        """
        models = [
            {"name": "gpt-4-turbo", "provider": "openai",
                "description": "GPT-4 Turbo Preview"},
            {"name": "gpt-4.1-mini", "provider": "openai",
                "description": "GPT-4o Mini (mapped to gpt-4o-mini)"},
            {"name": "gpt-4o-mini", "provider": "openai",
                "description": "GPT-4o Mini"},
            {"name": "local-llama-3", "provider": "ollama/lmstudio",
                "description": "LLaMA 3 (via LMStudio or Ollama)"},
            {"name": "local-mistral", "provider": "ollama/lmstudio",
                "description": "Mistral (via LMStudio or Ollama)"},
        ]

        result = []
        for model in models:
            # Quick availability check
            if model["provider"] == "openai":
                status = "available" if self.openai_api_key else "unavailable"
            else:
                # For local models, assume available (actual check would be expensive)
                status = "available"

            result.append({
                "name": model["name"],
                "status": status,
                "provider": model["provider"],
                "description": model["description"]
            })

        return result

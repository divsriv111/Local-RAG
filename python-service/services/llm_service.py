from typing import Generator, Optional
import time

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema import BaseMessage, HumanMessage, AIMessage

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

    def get_llm(self, model_name: Optional[str] = None, streaming: bool = False):
        """
        Get LLM instance based on model name.

        Args:
            model_name: Name of the model to use
            streaming: Whether to enable streaming

        Returns:
            LLM instance
        """
        model = model_name or self.default_model

        logger.info(f"Initializing LLM: {model}, streaming: {streaming}")

        try:
            # OpenAI models (GPT-4, GPT-4o-mini, etc.)
            if model.startswith("gpt-") or model.startswith("o1-"):
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key not configured")

                return ChatOpenAI(
                    model_name=model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=self.openai_api_key,
                    streaming=streaming
                )

            # Local models via LMStudio (OpenAI-compatible API)
            elif model.startswith("local-") and "lmstudio" in model.lower():
                model_name_clean = model.replace(
                    "local-", "").replace("-lmstudio", "")

                return ChatOpenAI(
                    model_name=model_name_clean,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    base_url=self.local_llm_base_url,
                    api_key="lm-studio",  # LMStudio doesn't require real key
                    streaming=streaming
                )

            # Local models via Ollama
            elif model.startswith("local-"):
                model_name_clean = model.replace("local-", "")

                return Ollama(
                    model=model_name_clean,
                    base_url=self.ollama_base_url,
                    temperature=self.temperature
                )

            # Default to GPT-4o-mini
            else:
                logger.warning(
                    f"Unknown model {model}, defaulting to gpt-4o-mini")
                return ChatOpenAI(
                    model_name="gpt-4o-mini",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=self.openai_api_key,
                    streaming=streaming
                )

        except Exception as e:
            logger.error(f"Error initializing LLM {model}: {str(e)}")
            raise

    def generate_response(
        self,
        query: str,
        context: str,
        model_name: Optional[str] = None,
        chat_history: Optional[list] = None
    ) -> str:
        """
        Generate response from LLM.

        Args:
            query: User query
            context: Context from retrieved documents
            model_name: Model to use
            chat_history: Previous conversation messages

        Returns:
            Generated response text
        """
        start_time = time.time()

        try:
            llm = self.get_llm(model_name, streaming=False)

            # Build prompt
            prompt = self._build_prompt(query, context, chat_history)

            # Generate response
            logger.info(
                f"Generating response with {model_name or self.default_model}")
            response = llm.invoke(prompt)

            # Extract text from response
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"Generated response in {elapsed_time:.2f}ms")

            return response_text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise

    def generate_response_stream(
        self,
        query: str,
        context: str,
        model_name: Optional[str] = None,
        chat_history: Optional[list] = None
    ) -> Generator[str, None, None]:
        """
        Generate streaming response from LLM.

        Args:
            query: User query
            context: Context from retrieved documents
            model_name: Model to use
            chat_history: Previous conversation messages

        Yields:
            Response tokens as they are generated
        """
        try:
            llm = self.get_llm(model_name, streaming=True)

            # Build prompt
            prompt = self._build_prompt(query, context, chat_history)

            logger.info(
                f"Starting streaming response with {model_name or self.default_model}")

            # Stream response
            for chunk in llm.stream(prompt):
                if hasattr(chunk, "content"):
                    yield chunk.content
                else:
                    yield str(chunk)

        except Exception as e:
            logger.error(
                f"Error in streaming response: {str(e)}", exc_info=True)
            yield f"Error: {str(e)}"

    def _build_prompt(
        self,
        query: str,
        context: str,
        chat_history: Optional[list] = None
    ) -> str:
        """
        Build prompt for LLM.

        Args:
            query: User query
            context: Context from documents
            chat_history: Previous messages

        Returns:
            Formatted prompt string
        """
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

        # Build full prompt
        prompt = f"""You are a helpful AI assistant. Answer the user's question based ONLY on the following context from PDF documents.
If the answer is not in the context, say "I don't have enough information to answer this question."

Context:
{context}

Previous conversation:
{history_text}

User question: {query}

Instructions:
- Provide a detailed and accurate answer
- Cite sources using [Source: filename.pdf, Page X] format
- Use markdown for formatting (bold, italic, lists, code blocks)
- Include clickable references at the end

Answer:"""

        return prompt

    def test_model(self, model_name: str) -> tuple[bool, str]:
        """
        Test if a model is available and working.

        Args:
            model_name: Model to test

        Returns:
            Tuple of (success, message)
        """
        try:
            llm = self.get_llm(model_name, streaming=False)

            # Send simple test query
            response = llm.invoke("Say 'Hello'")

            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            if response_text:
                return True, f"Model {model_name} is available"
            else:
                return False, f"Model {model_name} returned empty response"

        except Exception as e:
            return False, f"Model {model_name} error: {str(e)}"

    def get_available_models(self) -> list[dict]:
        """
        Get list of available models with their status.

        Returns:
            List of model info dictionaries
        """
        models = [
            {"name": "gpt-4-turbo", "provider": "openai"},
            {"name": "gpt-4o-mini", "provider": "openai"},
            {"name": "local-llama-3", "provider": "ollama"},
            {"name": "local-mistral", "provider": "ollama"},
            {"name": "local-llama-3-lmstudio", "provider": "lmstudio"},
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
                "provider": model["provider"]
            })

        return result

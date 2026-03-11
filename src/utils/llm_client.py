"""LLM Client abstraction for Vertex AI / Gemini models."""


import structlog
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings

logger = structlog.get_logger()

class LLMClient:
    """Async wrapper around Gemini LLMs via Vertex AI."""
    
    def __init__(self) -> None:
        self.model_name = settings.llm_model
        self._client = ChatVertexAI(
            model_name = settings.llm_model,
            project = settings.gcp_project_id,
            location = settings.gcp_location,
            temperature = settings.llm_temperature,
            max_output_tokens = settings.llm_max_tokens,
        )

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Send a prompt to Gemini LLM and return the text response.
        
        Args:
            prompt: The user prompt to send to the LLM.
            system: Optional system instructions for the LLM to prepend.

        Returns:
            The text response from the LLM.
        
        """
        messages = []

        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))

        logger.debug("llm_generate_start", model = self.model_name, prompt_length = len(prompt))
        response = await self._client.ainvoke(messages)        
        result = response.content
        logger.debug("llm_generate_end", model = self.model_name, response_length = len(result))
        return result

"""    
    async def generate_with_context(self, question: str, context: str, system: str | None = None) -> str:
        \"\"\"Generate a response using retrieved context (for RAG use cases).
        
        Args:
            question: The user question to send to the LLM.
            context: Retrieved document chunks joined as context.
            system: Optional system prompt override

        Returns:
            The model's grounded response.
        \"\"\"

        from src.prompts.templates import PromptTemplateManager
        prompts = PromptTemplateManager()
        prompt = prompts.render_rag(question=question, context=context)
        return await self.generate(prompt, system=system)

"""
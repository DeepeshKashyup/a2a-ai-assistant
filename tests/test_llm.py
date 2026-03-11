import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.utils.llm_client import LLMClient


@pytest.mark.asyncio
async def test_generate_returns_string() -> None:
    """Test LLMClient.generate returns a non-empty string."""
    with patch("src.utils.llm_client.ChatVertexAI") as mock_vertexai:
        mock_instance = MagicMock()
        mock_instance.ainvoke = AsyncMock(return_value=MagicMock(content="Paris is the capital of France."))
        mock_vertexai.return_value = mock_instance

        llm_client = LLMClient()
        response = await llm_client.generate("What is the capital of France?")

    assert isinstance(response, str)
    assert len(response) > 0